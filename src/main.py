from __future__ import annotations

import config

from api import handlers
from api import limiter

from contextlib import asynccontextmanager
from fastapi import FastAPI
from services import MemoryStore

"""
This is scheduled for deletion :) Im planning on using Redis instead
"""
@asynccontextmanager
async def lifespan(_api: FastAPI):
    store: MemoryStore = MemoryStore()
    await store.startup()
    _api.state.store = store
    try:
        yield
    finally:
        await store.shutdown()

api: FastAPI = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    summary=config.API_SUMMARY,
    lifespan=lifespan
)

api.state.limiter = limiter
handlers.register_exception_handlers(api)
handlers.register_middleware_handlers(api)