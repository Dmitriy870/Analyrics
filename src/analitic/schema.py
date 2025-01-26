from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoModel(BaseModel):
    id: PyObjectId | None = Field(None, alias="_id")

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True


class UserInfo(BaseModel):
    id: UUID = Field(...)
    created_at: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)
    is_approved: bool = Field(...)
    is_globally_blocked: bool = Field(...)
    role_id: UUID = Field(...)


class ProjectUserInfo(BaseModel):
    id: UUID = Field(...)
    created_at: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)
    project_id: UUID | None = Field(None)
    user_id: UUID | None = Field(None, alias="user")
    position_id: UUID | None = Field(None, alias="position")
    role: str | None = Field(None)
    is_blocked: bool = Field(default=False)
    blocked_by: UUID | None = Field(None)


class ProjectInfo(BaseModel):
    id: UUID = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    status: str = Field(...)
    created_by: UUID = Field(...)
    created_at: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)


class TaskInfo(BaseModel):
    id: UUID = Field(...)
    created_at: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)
    title: str = Field(...)
    description: str = Field(...)
    status: str = Field(...)
    assignee: UUID = Field(...)
    project_id: UUID | None = Field(None, alias="project")
    created_by: UUID = Field(...)


class Event(MongoModel):
    event_type: str = Field(...)
    user_id: UUID | None = Field(None)
    project_info: ProjectInfo | None = Field(None)
    task_info: TaskInfo | None = Field(None)
    project_user_info: ProjectUserInfo | None = Field(None)
    event_data: Dict[str, Any] | None = Field(None)
    received_at: datetime = Field(default_factory=datetime.utcnow)
