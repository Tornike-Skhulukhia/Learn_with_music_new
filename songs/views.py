import json
import re
import uuid
from urllib.parse import parse_qs, urlparse

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rabbitmq_workers.config import FANOUT_EXCHANGE_NAME, RABBITMQ_HOST
from rabbitmq_workers.producer import (
    send_fanout_message as add_message_to_fanout_queue,
)

from .helper_funcs import _get_youtube_video_id_from_url
from .models import Song


class Home(ListView):
    template_name = "songs/home.html"
    model = Song

    def get_queryset(self):
        q = super().get_queryset().order_by("-updated_at")[:20]

        return q


class AddSong(CreateView):
    template_name = "songs/add_song.html"
    model = Song

    fields = [
        "youtube_url",
        "subtitles_source_url",
        "custom_name",
    ]

    def form_valid(self, form):

        # make sure youtube url seems valid
        youtube_id = _get_youtube_video_id_from_url(form["youtube_url"].data)

        if youtube_id is None:
            form.add_error(
                "youtube_url",
                "Youtube url does not seem correct, it must have form: https://www.youtube.com/watch?v=TO-_3tck2tg",
            )

            return super().form_invalid(form)
        else:
            form.instance.youtube_id = youtube_id

        # make sure subtitles url seems valid if present
        if form["subtitles_source_url"].data:

            # for now just check that url seems valid youtube video url
            if not (
                _get_youtube_video_id_from_url(
                    form["subtitles_source_url"].data
                )
            ):

                form.add_error(
                    "subtitles_source_url",
                    "No supported subtitles found on given url, please try another one, currently youtube videos are supported",
                )

                return super().form_invalid(form)

        form.instance.save()

        # to download audio file for given song
        add_message_to_fanout_queue(
            rabbitmq_host=RABBITMQ_HOST,
            exchange_name=FANOUT_EXCHANGE_NAME,
            message=json.dumps(
                {
                    "action_id": str(uuid.uuid4()),
                    "action_type": "AUDIO_DOWNLOAD_FROM_YOUTUBE",
                    "song_id": form.instance.pk,
                    "destination_url": form.instance.youtube_url,
                }
            ),
        )

        # to download lyrics/subtitles for given song
        if form["subtitles_source_url"].data:
            add_message_to_fanout_queue(
                rabbitmq_host=RABBITMQ_HOST,
                exchange_name=FANOUT_EXCHANGE_NAME,
                message=json.dumps(
                    {
                        "action_id": str(uuid.uuid4()),
                        "action_type": "SUBTITLES_DOWNLOAD",
                        "song_id": form.instance.pk,
                        "destination_url": form.instance.subtitles_source_url,
                    }
                ),
            )
        else:
            # for now, if no specific subtitles-having youtube video or other source url
            # provided, try to get subtitles from youtube url of audio
            add_message_to_fanout_queue(
                rabbitmq_host=RABBITMQ_HOST,
                exchange_name=FANOUT_EXCHANGE_NAME,
                message=json.dumps(
                    {
                        "action_id": str(uuid.uuid4()),
                        "action_type": "SUBTITLES_DOWNLOAD",
                        "song_id": form.instance.pk,
                        "destination_url": form.instance.youtube_url,
                    }
                ),
            )

        # feedback message for user
        messages.success(self.request, "Song Successfully Created!")

        return super().form_valid(form)


class ViewSongDetail(DetailView):
    template_name = "songs/view_song_detail.html"
    model = Song


class DeleteSong(DeleteView):
    template_name = "songs/delete_song.html"
    model = Song

    success_url = reverse_lazy("songs_home")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Deleted Successfully!")

        # TODO: remove its audio file also when deleting song

        return super().post(request, *args, **kwargs)


class UpdateSong(View):
    template_name = "songs/edit_song.html"
    # fields = ["custom_name", "lyrics_and_timings"]

    def _get_context_dict(self, song):

        # show lyrics like csv for now, later may add better UI to edit it
        lyrics = []

        for i in song.lyrics_and_timings:
            lyrics.append(
                f'{i["text"].strip()}, {i["start"] / 1000}, {i["end"] / 1000}'
            )

        lyrics = "\n".join(lyrics)

        return {
            "custom_name": song.custom_name,
            "lyrics": lyrics,
            "title": song.title,
        }

    def _save_lyrics(
        self,
        song,
        lyrics_data,
    ):

        # try to use texts and start and end times
        line_texts, start_times, durations = [], [], []

        pattern = r"(.*?)\s*,\s*([0-9]+\.[0-9]+)\s*,\s*([0-9]+\.[0-9]+)$"

        for line in lyrics_data.split("\n"):
            line = line.strip()
            if not line:
                continue

            if match := re.search(pattern, line):
                text, start, end = match.groups()

                line_texts.append(text)
                start_times.append(float(start))
                durations.append(float(end) - start_times[-1])

            else:
                # not all lines have correct text, start, end structure
                # so save just texts only
                song.set_lyrics_without_timing_info(lyrics_data.split("\n"))
                return

        # save using seconds
        transcript = [
            {"text": i, "start": j, "duration": k}
            for i, j, k in zip(line_texts, start_times, durations)
        ]

        song.set_lyrics_using_timing_info_in_seconds(transcript)

    def post(self, request, *args, **kwargs):
        song = Song.objects.get(id=kwargs["pk"])

        posted_data = {i: j[0].strip() for i, j in dict(request.POST).items()}

        # all required args must be submitted from form
        if any([i not in posted_data for i in ["custom_name", "lyrics"]]):
            messages.warning(request, "Invalid Request!")

        else:
            self._save_lyrics(song, posted_data["lyrics"])

            song.custom_name = posted_data["custom_name"]

            song.save(update_fields=["custom_name"])

            messages.success(request, "Updated Successfully!")

        return render(
            request,
            self.template_name,
            self._get_context_dict(song),
        )

    def get(self, request, *args, **kwargs):
        song = Song.objects.get(id=kwargs["pk"])

        return render(
            request,
            self.template_name,
            self._get_context_dict(song),
        )


class ListenToSong(View):
    def get(self, request, *args, **kwargs):

        song = Song.objects.get(id=kwargs["pk"])

        song_data = {
            "lyrics_data": song.lyrics_and_timings,
            "youtube_image": song.youtube_image,
            "audio_source": song.absolute_static_url_of_audio_file,
        }

        return render(
            request,
            "songs/listen_to_song.html",
            {
                "song_data": json.dumps(song_data, ensure_ascii=False),
                "song_title": song.title,
            },
        )

    def post(self, request, *args, **kwargs):

        song = Song.objects.get(id=kwargs["pk"])
        updates_to_apply = json.loads(request.body)["data"]

        try:
            song.update_existing_lyrics_timings_using_only_start_and_end_times(
                updates_to_apply
            )

            return JsonResponse({"success": True})

        except AssertionError:
            return JsonResponse({"success": False})
