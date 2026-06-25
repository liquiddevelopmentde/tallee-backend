from __future__ import annotations

import config

from contextlib import asynccontextmanager
from core.limiter import limiter
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.responses import JSONResponse
from services import MemoryStore
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(api: FastAPI):
    store: MemoryStore = MemoryStore()
    await store.startup()
    api.state.store = store
    try:
        yield
    finally:
        await store.shutdown()


def main() -> None:
    api: FastAPI = FastAPI(
        title=config.API_TITLE,
        version=config.API_VERSION,
        summary=config.API_SUMMARY,
        lifespan=lifespan
    )
    api.state.limiter = limiter

    @api.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler() -> Response:
        """
        Handles rate limit exceptions
        :return: JSONResponse
        """
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again shortly."})

    @api.middleware("http")
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
                too_large = int(content_length) > config.API_REQUEST_MAX_PAYLOAD_BYTES
            except ValueError:
                too_large = False
            if too_large:
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"Request payload exceeds the maximum allowed size"},
                )
        return await call_next(request)


if __name__ == "__main__":
    main()