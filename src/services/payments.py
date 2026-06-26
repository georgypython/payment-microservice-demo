from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.payment import CreatePaymentSchema
from src.models import PaymentOrm, OutboxEventOrm
from src.models.enums import PaymentStatus


class PaymentsService:
    def __init__(
        self, session: AsyncSession, broker: RabbitBroker, queue: str, exchange: str
    ) -> None:
        self.session = session
        self.broker = broker
        self.queue = queue
        self.exchange = exchange

    async def create_payment(self, payment: CreatePaymentSchema, idempotency_key: str):
        payment_orm = PaymentOrm(
            idempotency_key=idempotency_key,
            status=PaymentStatus.PENDING,
            **payment.model_dump(),
        )
        self.session.add(payment_orm)
        await self.session.flush()

        outbox_event_orm = OutboxEventOrm(
            payment_id=payment_orm.id,
            exchange=self.exchange,
            queue=self.queue,
            is_processed=False,
        )
        self.session.add(outbox_event_orm)
        await self.session.commit()
