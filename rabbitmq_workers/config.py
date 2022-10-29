import os


# useful variables
FANOUT_EXCHANGE_NAME = "song_added"

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
