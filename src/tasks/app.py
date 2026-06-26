from faststream import FastStream
from dishka.integrations.faststream import setup_dishka

from src.dependencies.container import container
from .broker import broker

app = FastStream(broker)


setup_dishka(container, app, auto_inject=True)
