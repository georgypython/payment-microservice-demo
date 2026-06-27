import asyncio
from datetime import datetime
import random

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payment import PaymentOrm
from src.schemas.payment import PaymentEventSchema, WebhookPayloadSchema
from src.models.enums import PaymentStatus
from src.core.logger_setup import logger


class PaymentProcessingService:
    def __init__(
        self, session: AsyncSession, http_client: AsyncClient, max_attempts: int = 3
    ) -> None:
        self.session = session
        self.http_client = http_client
        self.max_attempts = max_attempts

    async def _complete_payment(self) -> PaymentStatus:
        await asyncio.sleep(random.uniform(2.0, 5.0))
        if random.random() < 0.9:
            return PaymentStatus.SUCCESS
        return PaymentStatus.FAILED

    async def _send_webhook(self, url: str, payload: WebhookPayloadSchema) -> bool:
        try:
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(
                f"Error while sending webhook: {e} for payment with id: {payload.id}"
            )
            return False

    async def process_new_payment(self, payment: PaymentEventSchema) -> bool:
        payment_id = payment.payment_id
        status = await self._complete_payment()

        payment_orm = await self.session.get(PaymentOrm, payment_id)

        if not payment_orm:
            logger.error(
                f"Payment with id: {id} finished with status: {status} and not found in db"
            )
            return False

        payment_orm.status = status
        payment_orm.processing_at = datetime.now()

        await self.session.commit()

        webhook_payload = WebhookPayloadSchema.model_validate(payment_orm)
        current_att = 0
        while current_att < self.max_attempts:
            result = await self._send_webhook(payment_orm.webhook_url, webhook_payload)
            if result:
                return True
            current_att += 1
            if current_att < self.max_attempts:
                delay = 2**current_att
                await asyncio.sleep(delay)

        logger.error(f"Payment with id: {id} not processed correctly")
        return False
