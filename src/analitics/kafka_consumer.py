import asyncio
import json

from aiokafka import AIOKafkaConsumer
from fastapi import Depends

from analitics.dependencies import get_analytics_service
from analitics.schema import EventType
from analitics.service import AnalyticsService
from config import KafkaConfig

kafka_config = KafkaConfig()


async def event_consume(service: AnalyticsService = Depends(get_analytics_service)):
    consumer = AIOKafkaConsumer(
        "events_topic",
        bootstrap_servers=kafka_config.KAFKA_BOOTSTRAP_SERVERS,
        group_id=kafka_config.KAFKA_GROUP_ID,
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event_data = json.loads(msg.value.decode("utf-8"))
            event_data["event_type"] = EventType.EVENT
            await service.process_event(event_data)
    finally:
        await consumer.stop()


async def model_consume(service: AnalyticsService = Depends(get_analytics_service)):
    consumer = AIOKafkaConsumer(
        "models_topic",
        bootstrap_servers=kafka_config.KAFKA_BOOTSTRAP_SERVERS,
        group_id=kafka_config.KAFKA_GROUP_ID,
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event_data = json.loads(msg.value.decode("utf-8"))
            event_data["event_type"] = EventType.MODEL
            await service.process_event(event_data)
    finally:
        await consumer.stop()


async def start_consumer_loop():
    loop = asyncio.get_event_loop()
    event_task = loop.create_task(event_consume())
    model_task = loop.create_task(model_consume())
    return event_task, model_task
