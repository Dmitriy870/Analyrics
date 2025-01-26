from pydantic import Field
from pydantic_settings import BaseSettings


class MongoConfig(BaseSettings):

    HOST: str = Field(...)
    PORT: int = Field(...)
    DB: str = Field(...)

    class Config:
        env_prefix = "MONGO_"


class KafkaConfig(BaseSettings):
    BOOTSTRAP_SERVERS: str = Field(...)
    GROUP_ID: str = Field(...)
    TOPIC: str = Field(...)

    class Config:
        env_prefix = "KAFKA_"


class VersionConfig(BaseSettings):
    API_V1_PREFIX: str = Field(default="/api/v1")
