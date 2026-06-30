"""
Redis-backed data storage
"""
from __future__ import annotations

import config

from .store import Store
from redis import asyncio as aioredis
from typing import Optional


class Redis:

    def __init__(self) -> None:
        self._pool: Optional[aioredis.ConnectionPool] = None

    async def connect(self) -> None:
        if config.REDIS_URL is None:
            raise RuntimeError("Redis URL not set")
        if config.REDIS_PORT is None:
            raise RuntimeError("Redis port not set")

        self._pool = aioredis.ConnectionPool.from_url(
            url=f"{config.REDIS_URL}:{config.REDIS_PORT}",
            max_connections=config.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.aclose()
            self._pool = None

    def get(self) -> Store:
        if self._pool is None:
            raise RuntimeError("Redis not connected")
        return Store(aioredis.Redis(connection_pool=self._pool))