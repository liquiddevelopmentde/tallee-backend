"""End-to-end tests for the match-sharing relay."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import config
from api.token import Token
from data import Entry


class _InMemoryStore:
    """Minimal in-memory store used to avoid a real Redis connection in tests."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    async def add(self, token: Token, payload: str, ttl: int) -> None:
        self._data[token.value] = payload

    async def get(self, token: Token) -> Entry | None:
        raw = self._data.get(token.value)
        return Entry(payload=raw) if raw is not None else None


def _make_redis_mock() -> MagicMock:
    store = _InMemoryStore()
    mock = MagicMock()
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    mock.get = MagicMock(return_value=store)
    return mock


@pytest.fixture
def client():
    with patch("main.Redis", return_value=_make_redis_mock()):
        from main import api
        with TestClient(api) as c:
            yield c


def _create(client, payload=None):
    payload = payload or {"g": "Catan", "p": [{"n": "Mathis", "s": 10}]}
    resp = client.post("/v1/shares/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json(), payload


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_returns_token_and_expiry(client):
    body, _ = _create(client)
    assert len(body["token"]) == 6
    assert body["ttl_seconds"] == config.TALLEE_SHARE_MAX_TTL
    assert "expires_at" in body


def test_create_read_roundtrip(client):
    body, payload = _create(client)
    resp = client.get(f"/v1/shares/{body['token']}")
    assert resp.status_code == 200
    assert resp.json()["payload"] == payload


def test_token_is_case_insensitive(client):
    body, payload = _create(client)
    resp = client.get(f"/v1/shares/{body['token'].lower()}")
    assert resp.status_code == 200
    assert resp.json()["payload"] == payload


def test_multiple_reads_allowed(client):
    body, _ = _create(client)
    for _ in range(3):
        assert client.get(f"/v1/shares/{body['token']}").status_code == 200


def test_unknown_token_is_404(client):
    assert client.get("/v1/shares/ZZZZZZ").status_code == 404


def test_malformed_token_is_404(client):
    # Wrong length → rejected before hitting the store.
    assert client.get("/v1/shares/abc").status_code == 404


def test_non_object_body_is_422(client):
    assert client.post("/v1/shares/", json=[1, 2, 3]).status_code == 422


def test_oversized_payload_is_413(client):
    limit = config.API_REQUEST_MAX_PAYLOAD_BYTES
    big = {"x": "a" * (limit + 10)}
    assert client.post("/v1/shares/", json=big).status_code == 413