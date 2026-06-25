from __future__ import annotations

import config

from api import handlers
from api import limiter
from fastapi import FastAPI


api: FastAPI = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    summary=config.API_SUMMARY
)

api.state.limiter = limiter
handlers.register_exception_handlers(api)
handlers.register_middleware_handlers(api)