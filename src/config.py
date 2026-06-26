import os
from dotenv import load_dotenv
load_dotenv()

from typing import Optional

REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
REDIS_PORT: Optional[str] = os.getenv("REDIS_PORT")

API_TITLE: str = "Tallee Match-Sharing Relay"
API_SUMMARY: str = "Relay for Tallee match data"
API_VERSION: str = "0.0.1"
API_REQUEST_MAX_PAYLOAD_BYTES: int = 256 * 1024  # 256 KB
API_REQUEST_RATE_LIMIT_CREATE: str = "20/minute"
API_REQUEST_RATE_LIMIT_HEALTH: str = "120/minute"
API_REQUEST_RATE_LIMIT_READ: str = "60/minute"
REDIS_MAX_CONNECTIONS: int = 20
TALLEE_SHARE_MAX_TTL: int = 60 * 10  # 10 Minutes
TALLEE_SHARE_TOKEN_LETTERS: str = "ABCDEFGHJKMNPQRSTUVWXYZ"
TALLEE_SHARE_TOKEN_NUMBERS: str = "23456789"
TALLEE_SHARE_TOKEN_ALPHABET: str = TALLEE_SHARE_TOKEN_LETTERS + TALLEE_SHARE_TOKEN_NUMBERS
TALLEE_SHARE_TOKEN_LENGTH: int = 6  # 6 Characters