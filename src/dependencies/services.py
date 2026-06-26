from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.dependencies.session import get_session
from src.tasks.broker import broker
from src.services import PaymentsService

# вернуть ебаную Dishka
async def get_payments_service(
    session: AsyncSession = Depends(get_session),
) -> PaymentsService:
    return PaymentsService(
        session,
        broker,
        queue=settings.payments.payment_queue,
        exchange=settings.payments.payment_exchange,
    )
