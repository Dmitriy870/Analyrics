from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from analitic.exceptions import EventNotFound
from analitic.schema import Event, ProjectInfo, ProjectUserInfo, TaskInfo, UserInfo


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db["users_analytics"]
        self.events_collection = db["events"]
        self.daily_stats_collection = db["daily_stats"]

    def _remove_event_type(self, event_data: dict) -> dict:
        event_data.pop("event_type", None)
        return event_data

    def _get_date_str(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d")

    async def _update_daily_stats(self, date_str: str, field: str, increment: int = 1) -> None:
        await self.daily_stats_collection.update_one(
            {"date": date_str}, {"$inc": {field: increment}}, upsert=True
        )

    async def process_event(self, event_data: dict) -> None:
        event_type = event_data.get("event_type")

        if not event_type:
            raise EventNotFound("Event type not found.")

        if event_type in ["user_created", "user_updated", "user_deleted"]:
            await self.process_user_event(event_data, event_type)
        elif event_type in ["project_created", "project_updated", "project_deleted"]:
            await self.process_project_event(event_data, event_type)
        elif event_type in [
            "add_user_on_project",
            "update_user_role_on_project",
            "delete_user_from_project",
        ]:
            await self.process_project_user_event(event_data, event_type)
        elif event_type.startswith("task_"):
            await self.process_task_event(event_data, event_type)

    async def process_user_event(self, event_data: dict, event_type: str) -> None:
        await self.save_raw_event_with_user(event_data, event_type)
        if event_type == "user_created":
            await self.handle_user_created(event_data)
        elif event_type == "user_updated":
            await self.handle_user_updated(event_data)
        elif event_type == "user_deleted":
            await self.handle_user_deleted(event_data)

    async def save_raw_event_with_user(self, event: dict, event_type: str) -> None:
        event = Event(event_type=event_type, user_id=event["user_id"])
        await self.events_collection.insert_one(event.model_dump(by_alias=True))

    async def handle_user_created(self, event_data: dict):
        event_data = self._remove_event_type(event_data)
        event_data.pop("role", None)
        user = UserInfo(**event_data)
        await self.users_collection.insert_one(user.model_dump(by_alias=True))

        date_str = self._get_date_str(event_data["received_at"])
        await self._update_daily_stats(date_str, "users_created_count")

    async def handle_user_updated(self, event_data: dict):
        event_data = self._remove_event_type(event_data)
        event_data.pop("role", None)

        user = UserInfo(**event_data)

        await self.users_collection.update_one(
            {"_id": user.id}, {"$set": user.model_dump(by_alias=True, exclude={"id"})}, upsert=True
        )

        date_str = self._get_date_str(event_data["received_at"])
        await self._update_daily_stats(date_str, "users_updated_count")

    async def handle_user_deleted(self, event_data: dict):
        event_data = self._remove_event_type(event_data)
        event_data.pop("role", None)
        user = UserInfo(**event_data)

        await self.users_collection.update_one(
            {"_id": user.id}, {"$set": {"deleted_at": event_data["received_at"]}}
        )

        date_str = self._get_date_str(event_data["received_at"])
        await self._update_daily_stats(date_str, "users_deleted_count")

    async def process_project_event(self, event_data: dict, event_type: str) -> None:
        await self.save_raw_event_with_project(event_data, event_type)

        if event_type == "project_created":
            await self.handle_project_created(event_data)
        elif event_type == "project_updated":
            await self.handle_project_updated(event_data)
        elif event_type == "project_deleted":
            await self.handle_project_deleted(event_data)

    async def save_raw_event_with_project(self, event_data: dict, event_type: str) -> None:
        event_data = self._remove_event_type(event_data)

        event = Event(
            event_type=event_type,
            project_info=ProjectInfo(**event_data),
        )
        await self.events_collection.insert_one(event.model_dump(by_alias=True))

    async def handle_project_created(self, event_data: dict) -> None:

        date_str = self._get_date_str(event_data["created_at"])
        await self._update_daily_stats(date_str, "projects_created_count")

    async def handle_project_updated(self, event_data: dict) -> None:

        date_str = self._get_date_str(event_data["updated_at"])
        await self._update_daily_stats(date_str, "projects_updated_count")

    async def handle_project_deleted(self, event_data: dict) -> None:

        date_str = self._get_date_str(event_data["updated_at"])
        await self._update_daily_stats(date_str, "projects_deleted_count")

    async def process_project_user_event(self, event_data: dict, event_type: str) -> None:
        await self.save_raw_event_with_project_user(event_data, event_type)

        if event_type == "add_user_on_project":
            await self.handle_project_user_added(event_data)
        elif event_type == "update_user_role_on_project":
            await self.handle_project_user_updated(event_data)
        elif event_type == "delete_user_from_project":
            await self.handle_project_user_deleted(event_data)

    async def save_raw_event_with_project_user(self, event_data: dict, event_type: str) -> None:
        event_data = self._remove_event_type(event_data)
        event = Event(
            event_type=event_type,
            user_id=event_data["user"],
            project_user_info=ProjectUserInfo(**event_data),
        )

        await self.events_collection.insert_one(event.model_dump(by_alias=True))

    async def handle_project_user_added(self, event_data: dict) -> None:

        date_str = self._get_date_str(event_data["created_at"])
        await self._update_daily_stats(date_str, "users_added_on_project_count")

    async def handle_project_user_updated(self, event_data: dict) -> None:

        date_str = self._get_date_str(event_data["updated_at"])
        await self._update_daily_stats(date_str, "project_users_updated_count")

    async def handle_project_user_deleted(self, event_data: dict) -> None:

        date_str = self._get_date_str(event_data["updated_at"])
        await self._update_daily_stats(date_str, "project_users_deleted_count")

    async def process_task_event(self, event_data: dict, event_type: str) -> None:
        await self.save_raw_event_with_task(event_data, event_type)

        if event_type == "task_created":
            await self.handle_task_created(event_data)
        elif event_type == "task_updated":
            await self.handle_task_updated(event_data)
        elif event_type == "task_deleted":
            await self.handle_task_deleted(event_data)

    async def save_raw_event_with_task(self, event_data: dict, event_type: str) -> None:
        event_data = self._remove_event_type(event_data)

        event = Event(
            event_type=event_type,
            user_id=event_data["user"],
            task_info=TaskInfo(**event_data),
        )

        await self.events_collection.insert_one(event.model_dump(by_alias=True))

    async def handle_task_created(self, event_data: dict) -> None:

        date_str = self._get_date_str(event_data["created_at"])
        await self._update_daily_stats(date_str, "tasks_created_count")

    async def handle_task_updated(self, event_data: dict) -> None:

        date_str = self._get_date_str(event_data["updated_at"])
        await self._update_daily_stats(date_str, "tasks_updated_count")

    async def handle_task_deleted(self, event_data: dict) -> None:

        date_str = self._get_date_str(event_data["updated_at"])
        await self._update_daily_stats(date_str, "tasks_deleted_count")
