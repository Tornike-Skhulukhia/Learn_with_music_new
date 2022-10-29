import logging

# initial stuff
import os

import django
from django.db import transaction
from youtube_transcript_api import YouTubeTranscriptApi

logging.basicConfig(
    format="%(asctime)s | %(funcName)s() | %(levelname)s | %(message)s",
    level=logging.INFO,
)

"""
Later add just subtitles url support and if it is withing
supported sites, like youtube, azlyrics e.t.c, try to get from there, otherwise
user can always add them or modify by hand using a bit more effort
"""

if __name__ == "__main__":
    from .common import _create_exchange_and_get_params
    from .config import FANOUT_EXCHANGE_NAME, RABBITMQ_HOST

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")
    django.setup()
    from songs.models import Song

    QUEUE_NAME = "youtube_subtitles_downloader"

    CONN, CHANNEL = _create_exchange_and_get_params(
        exchange_name=FANOUT_EXCHANGE_NAME,
        exchange_type="fanout",
        rabbitmq_host=RABBITMQ_HOST,
    )

    # actual functions

    def _get_youtube_video_transcript(video_id):
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        return transcript

    def callback(ch, method, properties, body):
        logging.info(f"Got {body=}")

        song_pk = body.decode("utf-8")

        # with transaction.atomic(durable=True):
        # song = Song.objects.select_for_update().filter(id=song_pk)

        song = Song.objects.filter(id=song_pk)
        if not song.exists():
            logging.info(f"Skipping not existent song {song_pk}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        song = song.get()

        if not song.subtitles_video_youtube_url:
            logging.info("No subtitles video url present, skipping download")
            return

        video_id = song.subtitles_video_youtube_id

        logging.info(
            f"Downloading youtube subtitles file for song {song_pk} using id {video_id}"
        )

        # change status in db for added song
        song._set_subtitles_download_status("Processing")

        try:
            transcripts = _get_youtube_video_transcript(video_id)

            song._update_info_using_youtube_transcripts(transcripts)
            song._set_subtitles_download_status("Downloaded")

            logging.info(
                f"Downloaded youtube transcript for video id {video_id}"
            )

        except Exception as e:
            logging.info(
                f"Can not download youtube subtitles with video id { video_id} exception was {e}"
            )
            # Failure
            song._set_subtitles_download_status("Failed")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Lets GO!

    CHANNEL.queue_declare(QUEUE_NAME, durable=True)
    CHANNEL.queue_bind(QUEUE_NAME, FANOUT_EXCHANGE_NAME)

    logging.info(f"[x] consumer for queue {QUEUE_NAME} is ready to go!")

    CHANNEL.basic_consume(
        queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False
    )

    CHANNEL.start_consuming()
