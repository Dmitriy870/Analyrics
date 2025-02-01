from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from analitics.schema import Event, EventType


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.events_collection = db["events"]
        self.daily_stats_collection = db["daily_stats"]

    async def process_event(self, event_data: dict) -> None:
        event = Event(**event_data)
        await self.save_event(event)

        if event.event_type == EventType.EVENT:
            await self.update_daily_stats(event.created_at, "events_count")
        elif event.event_type == EventType.MODEL:
            await self.process_model_event(event)

    async def save_event(self, event: Event) -> None:
        await self.events_collection.insert_one(event.model_dump(by_alias=True))

    async def process_model_event(self, event: Event) -> None:
        if event.event_name.startswith("get_"):
            await self.update_daily_stats(event.created_at, f"{event.model_type}_get_count")
        if event.event_name.startswith("create_"):
            await self.update_daily_stats(event.created_at, f"{event.model_type}_created_count")
        elif event.event_name.startswith("update_"):
            await self.update_daily_stats(event.created_at, f"{event.model_type}_updated_count")
        elif event.event_name.startswith("delete_"):
            await self.update_daily_stats(event.created_at, f"{event.model_type}_deleted_count")

    async def update_daily_stats(self, dt: datetime, field: str, increment: int = 1) -> None:
        date_str = dt.strftime("%Y-%m-%d")
        await self.daily_stats_collection.update_one(
            {"date": date_str}, {"$inc": {field: increment}}, upsert=True
        )
