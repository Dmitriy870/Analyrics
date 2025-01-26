from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from service import AnalyticsService

from database import get_mongo_db


async def get_analytics_service(
    db: AsyncIOMotorDatabase = Depends(get_mongo_db),
) -> AnalyticsService:
    return AnalyticsService(db)
