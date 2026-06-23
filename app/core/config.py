"""Application configuration for the tallee match-sharing relay.

Values are read from environment variables (or a local ``.env`` file). See
``.env.example`` for the full list. The defaults make the service run out of the
box with the in-memory store and no external dependencies.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Hard ceiling for how long a share may live on the server.
MAX_TTL_SECONDS = 600


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # How long an uploaded match stays retrievable. Capped at MAX_TTL_SECONDS.
    ttl_seconds: int = Field(default=600, ge=1)

    # Reject payloads larger than this (bytes). Match JSON is tiny, so 256 KB is
    # generous while still blocking abuse.
    max_payload_bytes: int = Field(default=256 * 1024, ge=1)

    # CORS origins allowed to call the API, "*" allows any.
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["*"])

    # Rate limits
    rate_limit_create: str = "20/minute"
    rate_limit_read: str = "60/minute"

    @field_validator("ttl_seconds")
    @classmethod
    def _cap_ttl(cls, value: int) -> int:
        return min(value, MAX_TTL_SECONDS)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
