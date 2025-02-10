import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from analitics.kafka_consumer import consume_messages
from analitics.router import router
from analitics.schema import KafkaTopic
from config import VersionConfig
from database import MongoDB

logger = logging.getLogger(__name__)
version_config = VersionConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDB.connect()
    consumer_event_task = asyncio.create_task(consume_messages(KafkaTopic.EVENTS_TOPIC.value))
    consumer_model_task = asyncio.create_task(consume_messages(KafkaTopic.MODELS_TOPIC.value))
    try:
        yield
    finally:
        consumer_model_task.cancel()
        consumer_event_task.cancel()
        try:
            await consumer_model_task
        except asyncio.CancelledError:
            logger.info("Consumer task is cancelled")
        try:
            await consumer_model_task
        except asyncio.CancelledError:
            logger.info("Consumer task is cancelled")


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix=version_config.API_V1_PREFIX)
