"""
Shared rate limiter instance.

Lives in its own module so both the app setup (main.py)
and the routers can import it without a circular import.
"""
from limits.strategies import RateLimiter
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter: RateLimiter = Limiter(key_func=get_remote_address).limiter
