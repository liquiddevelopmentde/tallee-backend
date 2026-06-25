"""HTTP routes for creating, fetching and revoking shared matches.

The match payload is handled opaquely — these routes never inspect player names
or scores; they only enforce size/format and hand the payload to the store.
"""
from __future__ import annotations

import config

from api import limiter
from core import tokens
from datetime import datetime
from datetime import timezone
from fastapi import APIRouter
from fastapi import Path
from fastapi import Request
from fastapi import Response
from fastapi.responses import JSONResponse
from schemas import ErrorResponse
from schemas import SharePayload
from schemas import ShareCreateResponse
from schemas import ShareResponse
from services import TokenCollisionError


router: APIRouter = APIRouter(prefix="/v1/shares")


@router.post(
    path="/create",
    response_model=ShareCreateResponse,
    status_code=201,
    responses={413: {"model": ErrorResponse}, 422: {"model": ErrorResponse}}
)
@limiter.limit(config.API_REQUEST_RATE_LIMIT_CREATE)
async def create(request: Request, payload: SharePayload)-> Response:
    try:
        record = await request.app.state.store.create(payload, config.TALLEE_SHARE_MAX_TTL)
    except TokenCollisionError:
        return JSONResponse(status_code=503, content={"detail": "Could not allocate a token"})

    return JSONResponse(
        status_code=201,
        content=ShareCreateResponse(
            token=record.token,
            expires_at=datetime.fromtimestamp(record.expires_atch, tz=timezone.utc),
            ttl_seconds=config.TALLEE_SHARE_MAX_TTL,
        ).model_dump(mode="json"),
    )


@router.get(
    "/{token}",
    response_model=ShareResponse,
    responses={404: {"model": ErrorResponse}, 410: {"model": ErrorResponse}},
)
@limiter.limit(config.API_REQUEST_RATE_LIMIT_READ)
async def get(request: Request, token: str = Path(..., min_length=1, max_length=16)) -> Response:
    normalized = tokens.normalize(token)
    if not tokens.is_valid(normalized):
        return JSONResponse(status_code=404, content={"detail": "Unknown or expired token."})

    record = await request.app.state.store.get(normalized)
    if record is None:
        return JSONResponse(status_code=404, content={"detail": "Unknown or expired token."})
    if record.is_expired:
        return JSONResponse(status_code=410, content={"detail": "This share has expired."})

    return JSONResponse(
        content=ShareResponse(
            payload=record.payload,
            created_at=datetime.fromtimestamp(record.created_at, tz=timezone.utc),
            expires_at=datetime.fromtimestamp(record.expires_at, tz=timezone.utc),
        ).model_dump(mode="json")
    )
