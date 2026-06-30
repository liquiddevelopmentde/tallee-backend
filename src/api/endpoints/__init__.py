"""
HTTP route definitions, one module per resource.

router aggregates every resource router so main mounts a single one.
"""

from fastapi import APIRouter

from . import health
from . import shares

router = APIRouter()
router.include_router(health.router)
router.include_router(shares.router)
