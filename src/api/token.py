"""
Short, human-friendly share tokens.

Tokens are what the user reads aloud, types, or encodes in a QR code, so the
alphabet excludes visually ambiguous characters (0/O, 1/I/L).

6 chars over a 31-symbol alphabet allow 887.503.681 unique combinations.
"""
from __future__ import annotations

import config
import secrets

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().upper()

        if (
            len(normalized) != config.TALLEE_SHARE_TOKEN_LENGTH
            or any(ch not in config.TALLEE_SHARE_TOKEN_ALPHABET for ch in normalized)
        ):
            raise ValueError(f"Invalid token: {self.value!r}")

        object.__setattr__(self, "value", normalized)

    @classmethod
    def generate(cls) -> Token:
        """
        Generate a new random token.

        The returned token is random but not guaranteed to be globally unique.
        """
        return cls(
            "".join(
                secrets.choice(config.TALLEE_SHARE_TOKEN_ALPHABET)
                for _ in range(config.TALLEE_SHARE_TOKEN_LENGTH)
            )
        )

    def __str__(self) -> str:
        return self.value