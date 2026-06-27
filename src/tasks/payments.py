from dishka.integrations.faststream import FromDishka

from src.schemas.payment import PaymentEventSchema
from src.services import PaymentProcessingService
from .broker import broker, main_queue


@broker.subscriber(queue=main_queue)
async def new_payment(
    message: PaymentEventSchema, service: FromDishka[PaymentProcessingService]
):
    result = await service.process_new_payment(message)
    if not result:
        raise ValueError("Payment Processing failed")
