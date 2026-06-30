"""
Health check endpoint
"""
from __future__ import annotations

import config

from ..limits import limiter
from fastapi import APIRouter
from fastapi import Request

router: APIRouter = APIRouter()


@router.get("/health")
@limiter.limit(config.API_REQUEST_RATE_LIMIT_HEALTH)
async def health(request: Request) -> dict[str, str]:
    return {"status": "ok"}
