"""
Stored entry returned from the data layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Entry:
    payload: Union[str, bytes]