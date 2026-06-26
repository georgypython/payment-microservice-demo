from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.session import get_session
from src.services import PaymentsService


async def get_payments_service(
    session: AsyncSession = Depends(get_session),
) -> PaymentsService:
    return PaymentsService(session)
