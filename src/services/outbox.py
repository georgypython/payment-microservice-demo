from typing import Sequence
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models import OutboxEventOrm
from src.core.logger_setup import logger


class OutboxService:
    def __init__(
        self,
        session: AsyncSession,
        broker: RabbitBroker,
        max_attempts: int,
        batch_size: int,
    ) -> None:
        self.session = session
        self.broker = broker
        self.max_attempts = max_attempts
        self.batch_size = batch_size

    async def _get_pending_events(self) -> Sequence[OutboxEventOrm]:
        stmt = (
            select(OutboxEventOrm)
            .where(
                OutboxEventOrm.is_processed == False,
                OutboxEventOrm.attempt < self.max_attempts,
            )
            .order_by(OutboxEventOrm.created_at.asc())
            .limit(self.batch_size)
            .with_for_update(skip_locked=True)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def publish_pending_events(self) -> None:
        events = await self._get_pending_events()
        if not events:
            return

        for event in events:
            try:
                await self.broker.publish(
                    message=event.message, queue=event.queue, exchange=event.exchange
                )
                event.is_processed = True
            except Exception as e:
                logger.warning(
                    f"Error while publishing event with id: {event.id} in outbox daemon. Current att: {event.attempt}. Error: {e}"
                )
                event.attempt += 1

        await self.session.commit()
