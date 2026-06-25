from __future__ import annotations

import config

from api import handlers
from api import limiter

from contextlib import asynccontextmanager
from fastapi import FastAPI
from services import MemoryStore


@asynccontextmanager
async def lifespan(api: FastAPI):
    store: MemoryStore = MemoryStore()
    await store.startup()
    api.state.store = store
    try:
        yield
    finally:
        await store.shutdown()


def main() -> None:
    api: FastAPI = FastAPI(
        title=config.API_TITLE,
        version=config.API_VERSION,
        summary=config.API_SUMMARY,
        lifespan=lifespan
    )
    api.state.limiter = limiter

    handlers.register_exception_handlers(api)
    handlers.register_middleware_handlers(api)


if __name__ == "__main__":
    main()