from faststream import Depends
from faststream.rabbit import RabbitRouter

from .broker import broker
from src.core.config import settings


@broker.subscriber(
    queue=settings.payments.payment_queue, 
    exchange=settings.payments.payment_exchange
)
async def new_payment(

):
