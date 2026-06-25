from __future__ import annotations

import config

from api import handlers
from api import limiter
from data import Redis
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis()
    await redis.connect()
    app.state.redis = redis
    yield
    await redis.disconnect()

api: FastAPI = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    summary=config.API_SUMMARY,
    lifespan=lifespan
)

api.state.limiter = limiter
handlers.register_exception_handlers(api)
handlers.register_middleware_handlers(api)