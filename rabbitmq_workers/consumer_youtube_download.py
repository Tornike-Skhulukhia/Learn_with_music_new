import logging

# initial stuff
import os

import django
from pytube import YouTube

logging.basicConfig(
    format="%(asctime)s | %(funcName)s() | %(levelname)s | %(message)s",
    level=logging.INFO,
)

if __name__ == "__main__":
    from .common import _create_exchange_and_get_params
    from .config import FANOUT_EXCHANGE_NAME, RABBITMQ_HOST

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")
    django.setup()
    from songs.models import Song

    QUEUE_NAME = "youtube_audio_downloader"

    CONN, CHANNEL = _create_exchange_and_get_params(
        exchange_name=FANOUT_EXCHANGE_NAME,
        exchange_type="fanout",
        rabbitmq_host=RABBITMQ_HOST,
    )

    # actual functions

    def _download_audio_using_youtube_video_id(video_id, filename):

        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")

        audio = yt.streams.filter(only_audio=True).first()

        out_file = audio.download(output_path="media/audio/", filename=filename)

        return yt

    def callback(ch, method, properties, body):
        logging.info(f"Got {body=}")

        song_pk = body.decode("utf-8")

        # ch.basic_ack(delivery_tag=method.delivery_tag)
        # return

        song = Song.objects.get(id=song_pk)

        video_id = song.youtube_id

        logging.info(
            f"Downloading audio file for song {song_pk} using id {video_id}"
        )

        # change status in db for added song
        song._set_audio_file_download_status("Processing")
        song.save()

        try:
            audio_filename = f"{video_id}.mp3"

            yt = _download_audio_using_youtube_video_id(
                video_id, filename=audio_filename
            )

            # Success | this function does Downloaded status set itself
            song._update_info_using_youtube_audio_download_object(
                yt, audio_filename
            )

            logging.info(
                f"From youtube downloaded audio with video id {video_id}"
            )

        except Exception as e:
            logging.info(
                f"Can not download youtube audio with video id { video_id} exception was {e}"
            )
            # Failure
            song._set_audio_file_download_status("Failed")

        song.save()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Lets GO!

    CHANNEL.queue_declare(QUEUE_NAME, durable=True)
    CHANNEL.queue_bind(QUEUE_NAME, FANOUT_EXCHANGE_NAME)

    logging.info(f"[x] consumer for queue {QUEUE_NAME} is ready to go!")

    CHANNEL.basic_consume(
        queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False
    )

    CHANNEL.start_consuming()
