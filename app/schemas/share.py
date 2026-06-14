"""API request/response schemas.

The match payload itself is treated opaquely — the relay never inspects player
names or scores — so it is typed as an arbitrary JSON object.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

SharePayload = dict[str, Any]


class ShareCreateResponse(BaseModel):
    token: str = Field(..., examples=["XF89J2"])
    expires_at: datetime
    ttl_seconds: int


class ShareResponse(BaseModel):
    payload: SharePayload
    created_at: datetime
    expires_at: datetime


class ErrorResponse(BaseModel):
    detail: str
