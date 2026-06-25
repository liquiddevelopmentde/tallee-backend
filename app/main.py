from __future__ import annotations

import config

from .core.config import Settings
from .core.limiter import limiter
from .services import MemoryStore
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


settings: Settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    store: MemoryStore = MemoryStore()
    await store.startup()
    app.state.store = store
    try:
        yield
    finally:
        await store.shutdown()


def main() -> None:
    app: FastAPI = FastAPI(
        title=config.API_TITLE,
        version=config.API_VERSION,
        summary=config.API_SUMMARY,
        lifespan=lifespan
    )
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler() -> Response:
        """
        Handles rate limit exceptions
        :return: JSONResponse
        """
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again shortly."})

    @app.middleware("http")
    async def _limit_body_size(request: Request, call_next):
        """
        Rejects requests exceeding the maximum allowed payload size.

        :param request: The incoming HTTP request.
        :param call_next: The next endpoint for the request.

        :return: A 413 JSON response if the payload exceeds the limit,
                 otherwise the response from the handler.
        """
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


if __name__ == "__main__":
    main()