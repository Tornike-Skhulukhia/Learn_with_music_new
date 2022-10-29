from django.conf import settings as django_app_settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinLengthValidator
from django.db import models as m
from django.urls import reverse

from .helper_funcs import _get_language_using_text


# Create your models here.
class Song(m.Model):
    AUDIO_FILE_DOWNLOAD_STATUSES = (
        ("0", "Initial"),
        ("1", "Processing"),
        ("2", "Downloaded"),
        ("-1", "Failed"),
    )

    youtube_url = m.CharField(max_length=128, default="")
    youtube_id = m.CharField(max_length=11)
    title = m.CharField(max_length=256)
    custom_name = m.CharField(max_length=256, blank=True, null=True)
    duration = m.SmallIntegerField(default=0)
    published_at = m.DateField(null=True, blank=True)
    # raw_lyrics = ArrayField(
    #     base_field=m.Text(max_length=128),
    #     null=True,
    #     blank=True,
    # )
    raw_lyrics = m.TextField(blank=True, null=True)

    created_at = m.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = m.DateTimeField(auto_now=True, null=True, blank=True)

    audio_file_download_status = m.CharField(
        max_length=2, choices=AUDIO_FILE_DOWNLOAD_STATUSES, default="0"
    )

    audio_file = m.FileField(upload_to="audio/", blank=True, null=True)
    youtube_video_metadata = m.JSONField(default=dict)

    created_by = m.ForeignKey(
        get_user_model(), on_delete=m.SET_NULL, blank=True, null=True
    )

    def _set_audio_file_download_status(self, status):
        statuses_to_values = {
            j: i for i, j in self.AUDIO_FILE_DOWNLOAD_STATUSES
        }

        self.audio_file_download_status = statuses_to_values[status]

    def _update_info_using_youtube_audio_download_object(
        self, yt, audio_filename
    ):
        # audio file stuff
        self._set_audio_file_download_status("Downloaded")

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

    @property
    def absolute_static_url_of_audio_file(self):
        if self.audio_file:
            return self.audio_file.path.replace("/app/", "/")
        return ""

    @property
    def youtube_image(self):
        return f"https://i3.ytimg.com/vi/{self.youtube_id}/hqdefault.jpg"

    def delete_lyrics(self):
        # remove all lines - later optimize to not delete all lines on each update
        return SongTextLine.objects.filter(song=self).delete()

    def add_lyrics(self, raw_lyrics):
        """
        Use this method to create SongTextLine objects for this song
        """
        initial_default_line_duration = 5000  # 5s

        for index, text in enumerate(raw_lyrics):
            language = Language.objects.get_or_create(
                id=_get_language_using_text(text)
            )[0]

            SongTextLine.objects.create(
                line_number=index + 1,
                text=text,
                start_time_millisecond=index * initial_default_line_duration,
                end_time_millisecond=(index + 1)
                * initial_default_line_duration,
                language=language,
                song=self,
            )

    def get_absolute_url(self):
        return reverse("view_song_detail", kwargs={"pk": self.id})

    @property
    def lyrics(self):
        """
        Easier to use in front format
        """

        # optimize later...
        lyrics = [
            {
                "start": i.start_time_millisecond,
                "end": i.end_time_millisecond,
                "text": i.text,
            }
            for i in self.songtextline_set.order_by("line_number").all()
        ]

        return lyrics

    def apply_lyrics_timing_update(self, updates_to_apply):

        # will be very slow, but working solution for now as MVP
        for info, line in zip(
            updates_to_apply,
            self.songtextline_set.order_by("line_number").all(),
        ):
            line.start_time_millisecond = info["s"]
            line.end_time_millisecond = info["e"]
            line.save()

    class Meta:
        constraints = [
            m.UniqueConstraint(
                fields=["created_by", "youtube_id"],
                name="unique_song_from_youtube_per_user",
            )
        ]

    def __str__(self):
        return self.title


class Language(m.Model):
    id = m.CharField(
        max_length=2, primary_key=True, validators=[MinLengthValidator(2)]
    )

    def __str__(self):
        return self.id


class SongTextLine(m.Model):
    line_number = m.SmallIntegerField()
    text = m.CharField(max_length=128)
    start_time_millisecond = m.IntegerField()
    end_time_millisecond = m.IntegerField(blank=True, null=True)
    language = m.ForeignKey(
        Language, on_delete=m.SET_NULL, null=True, blank=True
    )
    song = m.ForeignKey(
        Song,
        on_delete=m.CASCADE,
    )

    def __str__(self):
        return f"{self.song} | line {self.line_number} | {self.text} |"
