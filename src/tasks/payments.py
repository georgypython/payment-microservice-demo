from faststream.rabbit import RabbitRouter
from dishka.integrations.faststream import FromDishka

from src.services import PaymentsService

router = RabbitRouter(prefix="payments")


@router.subscriber(queue="new")
async def new_payment(service: FromDishka[PaymentsService]):
    pass
