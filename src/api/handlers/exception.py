"""
This file contains all api exception handlers
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi import Response
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


def register_exception_handlers(api: FastAPI) -> None:

    @api.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler() -> Response:
        """
        Handles rate limit exceptions
        :return: JSONResponse
        """
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again shortly."})
