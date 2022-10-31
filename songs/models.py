import copy
import re

from django.conf import settings as django_app_settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinLengthValidator
from django.db import models as m
from django.urls import reverse

# from .helper_funcs import _get_language_using_text


# Create your models here.
class Song(m.Model):
    DOWNLOAD_STATUSES = (
        ("Initial", "Initial"),
        ("Processing", "Processing"),
        ("Downloaded", "Downloaded"),
        ("Failed", "Failed"),
    )

    # song and lyrics sources | we may decide to add other audio sources besides youtube later
    youtube_url = m.CharField(max_length=128, default="")
    youtube_id = m.CharField(max_length=11)

    subtitles_source_url = m.CharField(
        max_length=128, default="", null=True, blank=True
    )

    # song & lyrics
    audio_file = m.FileField(upload_to="audio/", blank=True, null=True)
    lyrics_and_timings = m.JSONField(default=dict)
    youtube_video_metadata = m.JSONField(default=dict)

    # song info
    title = m.CharField(max_length=256)
    duration = m.SmallIntegerField(default=0)
    published_at = m.DateField(null=True, blank=True)

    # statuses
    audio_file_download_status = m.CharField(
        max_length=16, choices=DOWNLOAD_STATUSES, default="Initial"
    )
    subtitles_download_status = m.CharField(
        max_length=16, choices=DOWNLOAD_STATUSES, default="Initial"
    )

    # user-defined data
    custom_name = m.CharField(max_length=256, blank=True, default="")

    # meta info
    created_at = m.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = m.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = m.ForeignKey(
        get_user_model(), on_delete=m.SET_NULL, blank=True, null=True
    )

    def _set_audio_file_download_status(self, status):

        self.audio_file_download_status = status
        self.save(update_fields=["audio_file_download_status"])

    def _set_subtitles_download_status(self, status):

        self.subtitles_download_status = status
        self.save(update_fields=["subtitles_download_status"])

    def _update_info_using_youtube_audio_download_object(
        self, yt, audio_filename
    ):

        # audio file stuff
        self.audio_file.name = str(
            django_app_settings.MEDIA_ROOT / "audio" / audio_filename
        )

        # general song info stuff
        self.title = yt.title
        self.published_at = yt.publish_date
        self.duration = yt.length

        # useful data for future stuff
        self.youtube_video_metadata = {
            "video_details": yt.vid_info["videoDetails"]
        }

        self.save(
            update_fields=[
                "audio_file",
                "title",
                "published_at",
                "duration",
                "youtube_video_metadata",
            ]
        )

    def set_lyrics_without_timing_info(
        self,
        raw_lyrics,
        initial_default_line_duration=5000,
    ):

        lyrics_and_timings = []

        for index, text in enumerate(raw_lyrics):
            lyrics_and_timings.append(
                {
                    "n": index + 1,
                    "text": text,
                    "start": index * initial_default_line_duration,
                    "end": (index + 1) * initial_default_line_duration,
                }
            )

        self.lyrics_and_timings = lyrics_and_timings
        self.save(update_fields=["lyrics_and_timings"])

    def update_existing_lyrics_timings_using_only_start_and_end_times(
        self, new_start_and_end_times_list
    ):
        """
        We do not send texts from front, but a sequence of new start and end times to save
        """

        assert len(self.lyrics_and_timings) == len(
            new_start_and_end_times_list
        ), f"Length of {len(self.lyrics_and_timings)=} and {len(new_start_and_end_times_list)=} must be same"

        new_lyrics_and_timings = []

        for i, j in zip(self.lyrics_and_timings, new_start_and_end_times_list):

            new_lyrics_and_timings.append(
                {
                    "n": i["n"],
                    "text": i["text"],
                    "start": j["start"],
                    "end": j["end"],
                }
            )

        self.lyrics_and_timings = new_lyrics_and_timings
        self.save(update_fields=["lyrics_and_timings"])

    def set_lyrics_using_timing_info_in_seconds(
        self, transcript, max_duration_in_ms_to_merge_with_previous_line=500
    ):
        """
        Think how to make seconds & milliseconds handling easier with less chance of bugs.

        transcript example:
            [
                {
                    'text': 'Hey there',
                    'start': 7.58,
                    'duration': 6.13
                },
                {
                    'text': 'how are you',
                    'start': 14.08,
                    'duration': 7.58
                },
            ]
        """
        # not modify original list
        transcript = copy.deepcopy(transcript)

        # add end keys, remove durations & convert to integers, floats are not reliable
        for i in transcript:
            i["end"] = i["start"] + i.pop("duration")
            i["start"] = int(i["start"] * 1000)
            i["end"] = int(i["end"] * 1000)

        # make sure blanks are filled with empty texts info
        new_transcript = []
        curr_start_time = 0

        for i in transcript:
            if i["start"] > curr_start_time:
                new_transcript.append(
                    {
                        "text": "",
                        "start": curr_start_time,
                        "end": i["start"],
                    }
                )
            new_transcript.append(i)
            curr_start_time = i["end"]

        # clean text | remove {some_text_here} and extra symbols
        for i in new_transcript:
            i["text"] = re.sub("[\{].*?[\}]|♪|♫", "", i["text"]).strip()

        # as it is not nice to have very short intervals of "" texts between lines

        refined_new_transcript = [new_transcript[0]]

        for i in new_transcript[1:]:
            if (
                i["end"] - i["start"]
                <= max_duration_in_ms_to_merge_with_previous_line
            ):
                # join info with previous line, do not add separate entry for this one
                last = refined_new_transcript[-1]

                last["text"] = (f'{last["text"]} {i["text"]}').strip()

                last["end"] = i["end"]

            else:
                refined_new_transcript.append(i)

        # finally add line numbers
        for index, i in enumerate(refined_new_transcript):
            i["n"] = index + 1

        self.lyrics_and_timings = refined_new_transcript
        self.save(update_fields=["lyrics_and_timings"])

    @property
    def absolute_static_url_of_audio_file(self):
        if self.audio_file:
            return self.audio_file.path.replace("/app/", "/")
        return ""

    @property
    def youtube_image(self):
        return f"https://i3.ytimg.com/vi/{self.youtube_id}/hqdefault.jpg"

    def get_absolute_url(self):
        return reverse("view_song_detail", kwargs={"pk": self.id})

    def __str__(self):
        return self.title
