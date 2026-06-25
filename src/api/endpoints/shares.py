"""
HTTP routes for creating, fetching and revoking shared matches.

The match payload is handled opaquely. These routes never inspect player names
or scores; they only enforce size/format and hand the payload to the store.
"""
from __future__ import annotations

import config

from ..limits import limiter
from fastapi import APIRouter
from fastapi import Request
from fastapi import Response


router: APIRouter = APIRouter(prefix="/v1/shares")


@router.post(path="/create")
@limiter.limit(config.API_REQUEST_RATE_LIMIT_CREATE)
async def create(request: Request, payload)-> Response:
    pass


@router.get(path="/{token}")
@limiter.limit(config.API_REQUEST_RATE_LIMIT_READ)
async def get(request: Request, token: str) -> Response:
    pass
