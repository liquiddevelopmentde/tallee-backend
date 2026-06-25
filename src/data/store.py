"""
All Data Entries
"""
from .entry import Entry
from api import Token
from redis import asyncio as aioredis
from typing import Optional
from typing import Union


class Store:

    def __init__(self, client: aioredis.Redis):
        self.client: aioredis.Redis = client

    async def add(self, token: Token, payload: str, ttl: int) -> None:
        await self.client.set(token.value, payload, ex=ttl)

    async def get(self, token: Token) -> Optional[Entry]:
        raw: Optional[Union[str, bytes]] = await self.client.get(token.value)
        if raw is None:
            return None
        return Entry(payload=raw)
