import json
from urllib.parse import parse_qs, urlparse

from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rabbitmq_workers.config import FANOUT_EXCHANGE_NAME, RABBITMQ_HOST
from rabbitmq_workers.producer import (
    send_fanout_message as add_message_to_fanout_queue,
)

from .models import Language, Song, SongTextLine


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
        "custom_name",
        # "title",
        # "published_at",
        # "duration",
        # "unique_words_in_lyrics",
    ]

    def form_valid(self, form):

        # make sure youtube url seems valid
        try:
            youtube_url = urlparse(form["youtube_url"].data)
            query = parse_qs(youtube_url.query)

            youtube_id = query["v"][0]

            assert len(youtube_id) == 11

            form.instance.youtube_id = youtube_id

            form.instance.save()

        except Exception as e:

            form.add_error(
                "youtube_url",
                "Youtube url does not seem correct, it must have form: https://www.youtube.com/watch?v=TO-_3tck2tg",
            )

            return super().form_invalid(form)

        add_message_to_fanout_queue(
            rabbitmq_host=RABBITMQ_HOST,
            exchange_name=FANOUT_EXCHANGE_NAME,
            message=str(form.instance.pk),
        )

        messages.success(self.request, "Song Successfully Created!")

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):

        return super().post(request, *args, **kwargs)


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


class UpdateSong(UpdateView):
    model = Song
    template_name = "songs/edit_song.html"
    fields = ["custom_name", "raw_lyrics"]

    def post(self, request, *args, **kwargs):
        messages.success(request, "Updated Successfully!")

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        # save individual line info in separate table with useful for playing format
        form.instance.save()  # to know PK in db

        # add transaction here and everywhere where we should have them,
        # for example here if we deleted all data and for some reason
        # can not add new ones, we should not make update
        # at all and rollback, not delete lyrics info and then show error !

        form.instance.delete_lyrics()
        form.instance.add_lyrics(form["raw_lyrics"].data.split("\n"))

        return super().form_valid(form)


class ListenToSong(View):
    def get(self, request, *args, **kwargs):
        print(f"{request=} {args=} {kwargs=}")

        song = Song.objects.get(id=kwargs["pk"])

        song_data = {
            "lyrics_data": song.lyrics,
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

        song.apply_lyrics_timing_update(updates_to_apply)

        return JsonResponse(
            {"success": True},
        )
