from faststream.rabbit import RabbitBroker

from src.core.config import settings

broker = RabbitBroker(
    url=settings.rabbit.url, 
    graceful_timeout=settings.rabbit.graceful_timeout,
    reconnect_interval=settings.rabbit.recconect_interval,
    fail_fast=settings.rabbit.fail_fast,
)
