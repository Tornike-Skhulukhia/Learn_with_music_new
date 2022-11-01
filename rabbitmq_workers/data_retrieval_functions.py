import logging
import os

from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse
from .decorators import display_start_time_passed_arguments_and_running_duration
from songs.helper_funcs import _get_youtube_video_id_from_url


@display_start_time_passed_arguments_and_running_duration
def _make_sure_audio_file_is_downloaded_for_youtube_video(video_id, filename):

    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")

    # if file already exiss, do not redownload it
    if os.path.isfile(os.path.join("media/audio/", filename)):
        logging.info(
            f"Same audio file already downloaded for video {video_id}, skipping redownload"
        )
    else:
        audio = yt.streams.filter(only_audio=True).first()

        audio.download(output_path="media/audio/", filename=filename)

        logging.info(
            f"From youtube downloaded audio file for video_id {video_id}"
        )

    return yt


@display_start_time_passed_arguments_and_running_duration
def _get_youtube_video_transcript(url):

    video_id = _get_youtube_video_id_from_url(url)

    transcript = YouTubeTranscriptApi.get_transcript(
        video_id,
        languages=(
            "en",
            "ge",
            "ru",
            "en-US",
            "en-GB",
            "ka-ge",
            "ka",
            "cn",
        ),
    )

    return transcript


def _get_transcript_using_url(url):
    website = urlparse(url.lower()).netloc.replace("www.", "")

    if website == "youtube.com" or website == "m.youtube.com":
        return _get_youtube_video_transcript(url)

    else:
        raise ValueError(
            f"Website {website} is not supported for transcripts retrieval (at least yet)"
        )
