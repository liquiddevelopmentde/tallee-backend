"""tallee Match-Sharing relay — an account-less, ephemeral mailbox.

The app uploads a compressed match JSON and receives a short token. Receivers
fetch the match by token (via QR scan, typed code, or deep link) until it
expires (max. 10 minutes) or is explicitly revoked. The server stores the
payload opaquely and never interprets its contents.

This module only wires the app together — routes live in ``app.api``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from .api import api_router
from .core.config import get_settings
from .core.limiter import limiter
from .services import MemoryStore

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = MemoryStore()
    await store.startup()
    app.state.store = store
    try:
        yield
    finally:
        await store.shutdown()


app = FastAPI(
    title="tallee Match-Sharing Relay",
    version="1.0.0",
    summary="Ephemeral, account-less relay for sharing tallee match data.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again shortly."})


@app.middleware("http")
async def _limit_body_size(request: Request, call_next):
    # Reject oversized uploads early via Content-Length, before the body is read.
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            too_large = int(content_length) > settings.max_payload_bytes
        except ValueError:
            too_large = False
        if too_large:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Payload exceeds {settings.max_payload_bytes} bytes."},
            )
    return await call_next(request)


app.include_router(api_router)
