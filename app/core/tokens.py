"""Short, human-friendly share tokens.

Tokens are what the user reads aloud, types, or encodes in a QR code, so the
alphabet excludes visually ambiguous characters (0/O, 1/I/L). 6 chars over a
30-symbol alphabet give ~729 million combinations — combined with the short TTL
and rate limiting, brute-forcing a live token is impractical.
"""

from __future__ import annotations

import config
import secrets

def new_token() -> str:
    """Return a single random token. No uniqueness guarantee on its own."""
    return "".join(secrets.choice(config.TALLEE_SHARE_TOKEN_ALPHABET) for _ in range(config.TALLEE_SHARE_TOKEN_LENGTH))


def normalize(token: str) -> str:
    """Normalize user-supplied input (QR/typed) to canonical token form.

    Uppercases and strips surrounding whitespace so "xf89j2 " maps to "XF89J2".
    """
    return token.strip().upper()


def is_valid(token: str) -> bool:
    """True if ``token`` has the right length and only allowed characters."""
    return len(token) == config.TALLEE_SHARE_TOKEN_LENGTH and all(ch in config.TALLEE_SHARE_TOKEN_ALPHABET for ch in token)
