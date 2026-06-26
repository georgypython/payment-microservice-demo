from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.exceptions.payments import IdempotencyKeyError
from src.schemas.payment import (
    CreatePaymentSchema,
    CreatedPaymentSchema,
    PaymentEventSchema,
)
from src.models import PaymentOrm, OutboxEventOrm
from src.models.enums import PaymentStatus
from src.core.logger_setup import logger


class PaymentsService:
    def __init__(
        self,
        session: AsyncSession,
        broker: RabbitBroker,
        queue: str,
        exchange: str,
        event_max_attempts: int = 3,
    ) -> None:
        self.session = session
        self.broker = broker
        self.queue = queue
        self.exchange = exchange
        self.event_max_attempts = event_max_attempts

    async def _add_new_outbox_event_orm(
        self, idempotency_key: str, message: dict[str, str], queue: str
    ) -> OutboxEventOrm:
        event_orm = OutboxEventOrm(
            idempotency_key=idempotency_key,
            exchange=self.exchange,
            queue=queue,
            attempt=0,
            max_attempts=self.event_max_attempts,
            message=message,
            is_processed=False,
        )
        self.session.add(event_orm)
        await self.session.flush()
        return event_orm

    async def _add_new_payment_orm(
        self, payment: CreatePaymentSchema, idempotency_key: str
    ) -> PaymentOrm:
        payment_orm = PaymentOrm(
            idempotency_key=idempotency_key,
            status=PaymentStatus.PENDING,
            **payment.model_dump(),
        )
        self.session.add(payment_orm)
        await self.session.flush()
        return payment_orm

    async def create_payment(
        self, payment: CreatePaymentSchema, idempotency_key: str
    ) -> CreatedPaymentSchema:
        try:
            payment_orm = await self._add_new_payment_orm(payment, idempotency_key)
            payment_id = payment_orm.id
            message = PaymentEventSchema(payment_id=payment_id)
            queue = self.queue + ".new"

            event_orm = await self._add_new_outbox_event_orm(
                idempotency_key, message.model_dump(), queue
            )
            await self.session.commit()
            logger.info(f"New payment with outbox created, id: {payment_id}")
        except IntegrityError as e:
            await self.session.rollback()
            logger.warning(f"Idempotency key conflict for key: {idempotency_key}")
            raise IdempotencyKeyError

        try:
            await self.broker.publish(
                message=message, queue=queue, exchange=self.exchange
            )
            event_orm.is_processed = True
            await self.session.commit()
        except Exception as e:
            logger.warning(
                f"Broker publish failed, message handles by daemon. Error: {e}"
            )
        return CreatedPaymentSchema(
            payment_id=payment_id,
            status=payment_orm.status,
            created_at=payment_orm.created_at,
        )
