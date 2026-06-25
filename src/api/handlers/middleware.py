"""
This file contains all middlware handlers
"""

from __future__ import annotations

import config

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse


def register_middleware_handlers(api: FastAPI) -> None:

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
