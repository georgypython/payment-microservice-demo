from faststream import FastStream
from dishka.integrations.faststream import setup_dishka

from src.dependencies.container import container
from src.infrastructure.broker import dlq_queue, main_queue, broker
from src.consumers import payments

app = FastStream(broker)


setup_dishka(container, app, auto_inject=True)


@app.after_startup
async def declare_queues():
    await broker.declare_queue(main_queue)
    await broker.declare_queue(dlq_queue)
