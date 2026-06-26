from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, status
from dishka.integrations.fastapi import FromDishka, DishkaRoute
from starlette.status import HTTP_404_NOT_FOUND

from src.dependencies.auth import require_api_key
from src.exceptions.payments import IdempotencyKeyError, NotFoundError
from src.schemas.payment import CreatePaymentSchema, NewPaymentResponseSchema
from src.services.payments import PaymentsService

router = APIRouter(
    dependencies=[Depends(require_api_key)],
    route_class=DishkaRoute,
)


@router.post(
    "", status_code=status.HTTP_202_ACCEPTED, response_model=NewPaymentResponseSchema
)
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


@router.get("/{payment_id}", status_code=status.HTTP_200_OK)
async def get_payment_info(
    payment_id: UUID,
    service: FromDishka[PaymentsService],
):
    try:
        return await service.get_payment_info(payment_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Payment not found")
