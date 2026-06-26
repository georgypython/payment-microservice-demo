from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.payment import CreatePaymentSchema


class PaymentsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_payment(self, payment: CreatePaymentSchema, idempotency_key: str):
        pass
