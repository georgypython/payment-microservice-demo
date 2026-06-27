from faststream.rabbit import RabbitBroker, RabbitQueue

from src.core.config import settings

broker = RabbitBroker(
    url=settings.rabbit.url,
    graceful_timeout=settings.rabbit.graceful_timeout,
    reconnect_interval=settings.rabbit.recconect_interval,
    fail_fast=settings.rabbit.fail_fast,
)

dlq_queue = RabbitQueue(name="payments.new.dlq", auto_delete=False)

main_queue = RabbitQueue(
    name="payments.new",
    auto_delete=False,
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": "payments.new.dlq",
    },
)
