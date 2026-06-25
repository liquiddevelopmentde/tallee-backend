"""In-memory ephemeral storage for shared matches.

Shares live in a single process: a dict holds them and a background task purges
expired entries. Data is lost on restart, which is acceptable for a 10-minute
"fire & forget" relay. This means the app must run with a single worker.

The store owns token generation so the collision check stays close to the data.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

from core import tokens

# How many times to retry on a token collision before giving up.
_MAX_TOKEN_ATTEMPTS = 10


@dataclass(frozen=True)
class ShareRecord:
    token: str
    payload: Any
    created_at: float  # epoch seconds
    expires_at: float  # epoch seconds

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at


class TokenCollisionError(RuntimeError):
    """Raised when a unique token could not be generated after several tries."""


class MemoryStore:
    """In-process store with a background purger for expired entries."""

    def __init__(self, purge_interval_seconds: float = 30.0) -> None:
        self._data: dict[str, ShareRecord] = {}
        self._lock = asyncio.Lock()
        self._purge_interval = purge_interval_seconds
        self._purge_task: asyncio.Task[None] | None = None

    async def startup(self) -> None:
        if self._purge_task is None:
            self._purge_task = asyncio.create_task(self._purge_loop())

    async def shutdown(self) -> None:
        if self._purge_task is not None:
            self._purge_task.cancel()
            try:
                await self._purge_task
            except asyncio.CancelledError:
                pass
            self._purge_task = None

    async def create(self, payload: Any, ttl_seconds: int) -> ShareRecord:
        now = time.time()
        async with self._lock:
            for _ in range(_MAX_TOKEN_ATTEMPTS):
                token = tokens.new_token()
                if token not in self._data:
                    record = ShareRecord(
                        token=token,
                        payload=payload,
                        created_at=now,
                        expires_at=now + ttl_seconds,
                    )
                    self._data[token] = record
                    return record
        raise TokenCollisionError("could not allocate a unique token")

    async def get(self, token: str) -> ShareRecord | None:
        record = self._data.get(token)
        if record is not None and record.is_expired:
            self._data.pop(token, None)
        return record

    async def delete(self, token: str) -> bool:
        return self._data.pop(token, None) is not None

    async def _purge_loop(self) -> None:
        while True:
            await asyncio.sleep(self._purge_interval)
            now = time.time()
            async with self._lock:
                expired = [t for t, r in self._data.items() if r.expires_at <= now]
                for token in expired:
                    self._data.pop(token, None)
