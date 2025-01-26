from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import MongoConfig

mongo_config = MongoConfig()


async def get_mongo_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client = AsyncIOMotorClient(mongo_config.HOST, mongo_config.PORT)
    db = client[mongo_config.DB]
    try:
        yield db
    finally:
        client.close()
