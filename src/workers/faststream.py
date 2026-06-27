from faststream import FastStream
from dishka.integrations.faststream import setup_dishka

from src.dependencies.container import container
from src.infrastructure import broker
from src.consumers import payments

app = FastStream(broker)


setup_dishka(container, app, auto_inject=True)
