import asyncio
from dishka import AsyncContainer

from src.services.outbox import OutboxService
from src.core.logger_setup import logger


async def outbox_daemon(container: AsyncContainer, sleep_delay: int) -> None:
    logger.info("Outbox daemon start recieve events")
    while True:
        try:
            async with container() as req_container:
                service = await req_container.get(OutboxService)
                await service.publish_pending_events()
        except Exception as e:
            logger.error(f"Outbox daemon error: {e}")

        await asyncio.sleep(sleep_delay)
