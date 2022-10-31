import json
import logging
import os
import traceback

import django

from .common import _create_exchange_and_get_params
from .config import FANOUT_EXCHANGE_NAME, RABBITMQ_HOST
from .data_retrieval_functions import (
    _make_sure_audio_file_is_downloaded_for_youtube_video,
    _get_transcript_using_url,
)
from .decorators import display_start_time_passed_arguments_and_running_duration
from songs.helper_funcs import _get_youtube_video_id_from_url

logging.basicConfig(
    format="%(asctime)s | %(funcName)s() | %(levelname)s | %(message)s",
    level=logging.INFO,
)

if __name__ == "__main__":

    # initialize things
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")
    django.setup()
    from songs.models import Song

    QUEUE_NAME = "audio_and_lyrics_downloader"

    CONN, CHANNEL = _create_exchange_and_get_params(
        exchange_name=FANOUT_EXCHANGE_NAME,
        exchange_type="fanout",
        rabbitmq_host=RABBITMQ_HOST,
    )

    # actual function
    @display_start_time_passed_arguments_and_running_duration
    def callback(ch, method, properties, body):
        payload = json.loads(body.decode("utf-8"))

        action_type = payload["action_type"]
        action_id = payload["action_id"]
        destination_url = payload["destination_url"]

        # make sure given song object exists in db
        song = Song.objects.filter(id=payload["song_id"])

        if not song.exists():
            logging.info(
                f"Skipping not existent song | {action_type=} | {action_id=}"
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # get it
        song = song.get()

        # function that will allow us to change statuses like processing, downloaded and finished
        _function_name_to_change_object_status = {
            "AUDIO_DOWNLOAD_FROM_YOUTUBE": "_set_audio_file_download_status",
            "SUBTITLES_DOWNLOAD": "_set_subtitles_download_status",
        }[payload["action_type"]]

        change_status_to = getattr(song, _function_name_to_change_object_status)

        change_status_to("Processing")

        try:
            if action_type == "AUDIO_DOWNLOAD_FROM_YOUTUBE":

                video_id = _get_youtube_video_id_from_url(destination_url)

                filename = f"{video_id}.mp3"

                yt = _make_sure_audio_file_is_downloaded_for_youtube_video(
                    video_id, filename=filename
                )

                song._update_info_using_youtube_audio_download_object(
                    yt, filename
                )

            elif action_type == "SUBTITLES_DOWNLOAD":

                transcripts = _get_transcript_using_url(destination_url)

                song.set_lyrics_using_timing_info_in_seconds(transcripts)

            change_status_to("Downloaded")

            logging.info(f"Action with id {action_id} finished successfully")

        except Exception:
            logging.info(
                f"Action with id {action_id} failed, reason: {repr(traceback.format_exc())}"
            )
            # Failure
            change_status_to("Failed")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    # connect things & GO!
    CHANNEL.queue_declare(QUEUE_NAME, durable=True)
    CHANNEL.queue_bind(QUEUE_NAME, FANOUT_EXCHANGE_NAME)

    logging.info(f"[x] consumer for queue {QUEUE_NAME} is ready to go!")

    CHANNEL.basic_consume(
        queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False
    )

    CHANNEL.start_consuming()
