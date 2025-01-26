import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from analitic.kafka_consumer import start_consumer_loop

# from auth.router import router as auth_router
from config import VersionConfig

version_config = VersionConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_consumer_loop())
    yield


app = FastAPI(lifespan=lifespan)

# app.include_router(auth_router, prefix=version_config.API_V1_PREFIX)
