from .common import _create_exchange_and_get_params
from .config import FANOUT_EXCHANGE_NAME, RABBITMQ_HOST


def send_fanout_message(rabbitmq_host, exchange_name, message):

    conn, channel = _create_exchange_and_get_params(
        rabbitmq_host, exchange_name, exchange_type="fanout"
    )

    channel.basic_publish(exchange=exchange_name, routing_key="", body=message)
    print(" [x] Sent message", message)

    conn.close()


if __name__ == "__main__":
    send_fanout_message(
        rabbitmq_host=RABBITMQ_HOST,
        exchange_name=FANOUT_EXCHANGE_NAME,
        message="TUVcZfQe-Kw",
    )
