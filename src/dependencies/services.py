from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.payments import PaymentsService
from src.tasks.broker import broker


class ServicesProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_payments_service(self, session: AsyncSession) -> PaymentsService:
        return PaymentsService(
            session,
            broker,
            queue="payments",
            exchange="",
            event_max_attempts=3,
        )
