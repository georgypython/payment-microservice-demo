from dishka import Provider, Scope, provide
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import PaymentAcceptanceService, PaymentProcessingService
from src.tasks.broker import broker


class ServicesProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_payment_acceptance_service(
        self, session: AsyncSession
    ) -> PaymentAcceptanceService:
        return PaymentAcceptanceService(
            session,
            broker,
            queue="payments.new",
            exchange="",
            event_max_attempts=3,
        )

    @provide(scope=Scope.REQUEST)
    async def get_payment_processing_service(
        self, session: AsyncSession, http_client: AsyncClient
    ) -> PaymentProcessingService:
        return PaymentProcessingService(session, http_client, max_attempts=3)
