from fastapi import APIRouter, Depends, Header, status
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.dependencies.auth import require_api_key
from src.schemas.payment import CreatePaymentSchema
from src.services.payments import PaymentsService

router = APIRouter(
    dependencies=[Depends(require_api_key)],
    route_class=DishkaRoute,
)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_new_payment(
    payment: CreatePaymentSchema,
    service: FromDishka[PaymentsService],
    idempotency_key: str = Header(..., alias="Idempotency-Key", max_length=64),
):
    result = await service.create_payment(payment, idempotency_key)
