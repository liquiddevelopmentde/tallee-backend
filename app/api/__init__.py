"""HTTP route definitions, one module per resource.

``api_router`` aggregates every resource router so ``main`` mounts a single one.
"""

from fastapi import APIRouter

from . import health, shares

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(shares.router)
