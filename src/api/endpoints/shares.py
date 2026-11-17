"""
HTTP routes for creating and fetching shared matches.

The match payload is handled opaquely. These routes never inspect player names
or scores; they only enforce size/format and hand the payload to the store.
"""
from __future__ import annotations

import config
import json

from ..limits import limiter
from ..token import Token
from data import Entry
from data import Store
from datetime import datetime
from datetime import timedelta
from datetime import UTC
from fastapi import APIRouter
from fastapi import Body
from fastapi import HTTPException
from fastapi import Request
from typing import Any
from typing import Dict
from typing import Optional


router: APIRouter = APIRouter(prefix="/v1/shares")

with open(config.DEBUG_MATCHES["DEBUGX"], encoding="utf-8") as f:
    DEBUG_MATCH_PAYLOAD: Dict[str, Any] = json.load(f)

DEBUG_MATCH_PAYLOADS: Dict[str, Dict[str, Any]] = {}
for _token_value, _path in config.DEBUG_MATCHES.items():
    with open(_path, encoding="utf-8") as _f:
        DEBUG_MATCH_PAYLOADS[_token_value] = json.load(_f)


@router.post(path="/", status_code=201)
@limiter.limit(config.API_REQUEST_RATE_LIMIT_CREATE)
async def create(request: Request, payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    store: Store = request.app.state.redis.get()
    token: Token = Token.generate()
    ttl: int = config.TALLEE_SHARE_MAX_TTL

    await store.add(token, json.dumps(payload), ttl)

    expires_at: str = (datetime.now(UTC) + timedelta(seconds=ttl)).isoformat()
    return {"token": token.value, "ttl_seconds": ttl, "expires_at": expires_at}


@router.get(path="/{token}")
@limiter.limit(config.API_REQUEST_RATE_LIMIT_READ)
async def get(request: Request, token: str) -> Dict[str, Any]:
    try:
        token: Token = Token(token)
    except ValueError as err:
        raise HTTPException(status_code=404) from err

    if token.value in DEBUG_MATCH_PAYLOADS:
        return {"payload": DEBUG_MATCH_PAYLOADS[token.value]}

    store: Store = request.app.state.redis.get()

    entry: Optional[Entry] = await store.get(token)

    if entry is None:
        raise HTTPException(status_code=404)
    return {"payload": json.loads(entry.payload)}
