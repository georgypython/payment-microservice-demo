from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import PaymentsService


class ServicesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_payments_service(self, session: AsyncSession) -> PaymentsService:
        return PaymentsService(session)
