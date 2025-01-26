import asyncio
import json

from aiokafka import AIOKafkaConsumer
from fastapi import Depends

from analitic.dependencies import get_analytics_service
from analitic.service import AnalyticsService
from config import KafkaConfig

kafka_config = KafkaConfig()


async def consume(service: AnalyticsService = Depends(get_analytics_service)):
    consumer = AIOKafkaConsumer(
        *[topic.strip() for topic in kafka_config.KAFKA_TOPICS.split(",")],
        bootstrap_servers=kafka_config.KAFKA_BOOTSTRAP_SERVERS,
        group_id=kafka_config.KAFKA_GROUP_ID
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event_data = json.loads(msg.value.decode("utf-8"))
            await service.process_event(event_data)
    finally:
        await consumer.stop()


async def start_consumer_loop():
    loop = asyncio.get_event_loop()
    task = loop.create_task(consume())
    return task
