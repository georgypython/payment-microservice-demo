from fastapi import APIRouter, Depends, Header, status

from src.dependencies.auth import require_api_key
from src.dependencies import get_payments_service
from src.schemas.payment import CreatePaymentSchema
from src.services.payments import PaymentsService

router = APIRouter(
    dependencies=[Depends(require_api_key)],
)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_new_payment(
    payment: CreatePaymentSchema,
    idempotency_key: str = Header(..., alias="Idempotency-Key", max_length=64),
    service: PaymentsService = Depends(get_payments_service),
):
    result = await service.create_payment(payment, idempotency_key)
