import pika


def _create_exchange_and_get_params(
    rabbitmq_host, exchange_name, exchange_type
):

    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host)
    )

    channel = conn.channel()

    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type=exchange_type,
        durable=True,
    )

    return conn, channel
