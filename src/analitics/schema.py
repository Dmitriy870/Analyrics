from datetime import datetime
from enum import Enum
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


class EventType(str, Enum):
    MODEL = "MODEL"
    EVENT = "EVENT"


class Event(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    event_type: EventType = Field(...)
    event_name: str = Field(...)
    received_by: str = Field(...)
    model_type: str | None = Field(None)
    model_data: Dict[str, Any] | None = Field(None)
    user_id: UUID | None = Field(None)
    project_id: UUID | None = Field(None)
    received_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
