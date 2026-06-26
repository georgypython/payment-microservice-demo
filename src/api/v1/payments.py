from fastapi import APIRouter, Depends, HTTPException, Header, status
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.dependencies.auth import require_api_key
from src.exceptions.payments import IdempotencyKeyError
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
    try:
        return await service.create_payment(payment, idempotency_key)
    except IdempotencyKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Idempotency key conflict"
        )
