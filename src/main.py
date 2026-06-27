import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from dishka.integrations.fastapi import setup_dishka

from src.api import router as api_router
from src.core.config import settings
from src.dependencies.container import container
from src.workers import outbox_daemon
from src.infrastructure import broker, db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    outbox_task = asyncio.create_task(
        outbox_daemon(container, settings.outbox.sleep_delay)
    )
    await broker.connect()

    yield

    outbox_task.cancel()
    try:
        await outbox_task
    except asyncio.CancelledError:
        pass

    await db_helper.dispose()
    await broker.stop()


app = FastAPI(
    lifespan=lifespan,
    title=settings.run.title,
)

setup_dishka(container=container, app=app)

app.include_router(api_router, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
