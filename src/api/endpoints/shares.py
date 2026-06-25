"""HTTP routes for creating, fetching and revoking shared matches.

The match payload is handled opaquely — these routes never inspect player names
or scores; they only enforce size/format and hand the payload to the store.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Body, Path, Request, Response
from fastapi.responses import JSONResponse

from core import tokens
from core.config import get_settings
from core.limiter import limiter
from schemas import ErrorResponse, SharePayload, ShareCreateResponse, ShareResponse
from services import TokenCollisionError

settings = get_settings()
router = APIRouter(prefix="/v1/shares", tags=["shares"])


def _to_dt(epoch: float) -> datetime:
    return datetime.fromtimestamp(epoch, tz=timezone.utc)


@router.post(
    "",
    response_model=ShareCreateResponse,
    status_code=201,
    responses={413: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
@limiter.limit(settings.rate_limit_create)
async def create_share(
    request: Request,
    payload: SharePayload = Body(
        ...,
        # A single shared match plus the entities it references (game, group,
        # players). The same top-level shape as the app's full export, filtered to
        # one match and without `statistics`. The server treats this opaquely —
        # IDs are sender-local join keys that the receiver remaps on import.
        examples=[
            {
                "players": [
                    {"id": "p1", "createdAt": "2026-06-01T10:00:00Z", "name": "Thomas", "description": "", "deleted": False},
                    {"id": "p2", "createdAt": "2026-06-01T10:00:00Z", "name": "Mark", "description": "", "deleted": False},
                ],
                "games": [
                    {"id": "g1", "createdAt": "2026-06-01T10:00:00Z", "name": "Catan", "ruleset": "", "description": "", "color": "#E07A5F", "icon": "dice"},
                ],
                "groups": [
                    {"id": "gr1", "createdAt": "2026-06-01T10:00:00Z", "name": "Spieleabend", "description": "", "memberIds": ["p1", "p2"]},
                ],
                "matches": [
                    {
                        "id": "m1",
                        "name": "Catan am 13.06.",
                        "createdAt": "2026-06-13T19:30:00Z",
                        "endedAt": "2026-06-13T21:00:00Z",
                        "gameId": "g1",
                        "groupId": "gr1",
                        "playerIds": ["p1", "p2"],
                        "scores": {
                            "p1": {"roundNumber": 0, "score": 10, "change": 10},
                            "p2": {"roundNumber": 0, "score": 8, "change": 8},
                        },
                        "notes": "",
                        "isTeamMatch": False,
                        "teams": None,
                    },
                ],
            }
        ],
    ),
) -> Response:
    # The body is declared as a typed parameter, so Swagger shows an editor, and
    # FastAPI returns 422 on invalid JSON or a non-object body automatically.
    # The size cap is enforced upstream by the body-size middleware in main.py.
    try:
        record = await request.app.state.store.create(payload, settings.ttl_seconds)
    except TokenCollisionError:
        return JSONResponse(status_code=503, content={"detail": "Could not allocate a token, retry."})

    return JSONResponse(
        status_code=201,
        content=ShareCreateResponse(
            token=record.token,
            expires_at=_to_dt(record.expires_at),
            ttl_seconds=settings.ttl_seconds,
        ).model_dump(mode="json"),
    )


@router.get(
    "/{token}",
    response_model=ShareResponse,
    responses={404: {"model": ErrorResponse}, 410: {"model": ErrorResponse}},
)
@limiter.limit(settings.rate_limit_read)
async def get_share(request: Request, token: str = Path(..., min_length=1, max_length=16)) -> Response:
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
            created_at=_to_dt(record.created_at),
            expires_at=_to_dt(record.expires_at),
        ).model_dump(mode="json")
    )


@router.delete(
    "/{token}",
    status_code=204,
    responses={404: {"model": ErrorResponse}},
)
@limiter.limit(settings.rate_limit_read)
async def delete_share(request: Request, token: str = Path(..., min_length=1, max_length=16)) -> Response:
    normalized = tokens.normalize(token)
    if not tokens.is_valid(normalized):
        return JSONResponse(status_code=404, content={"detail": "Unknown token."})

    removed = await request.app.state.store.delete(normalized)
    if not removed:
        return JSONResponse(status_code=404, content={"detail": "Unknown token."})
    return Response(status_code=204)
