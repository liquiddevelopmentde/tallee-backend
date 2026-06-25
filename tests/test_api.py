"""End-to-end tests for the match-sharing relay (in-memory store)."""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from src.core.config import get_settings
from src.main import app
from src.services import MemoryStore


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _create(client, payload=None):
    payload = payload or {"g": "Catan", "p": [{"n": "Mathis", "s": 10}]}
    resp = client.post("/v1/shares", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json(), payload


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_returns_token_and_expiry(client):
    body, _ = _create(client)
    assert len(body["token"]) == 6
    assert body["ttl_seconds"] == get_settings().ttl_seconds
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
    # Contains excluded chars / wrong length → rejected before hitting the store.
    assert client.get("/v1/shares/abc").status_code == 404


def test_non_object_body_is_422(client):
    assert client.post("/v1/shares", json=[1, 2, 3]).status_code == 422


def test_oversized_payload_is_413(client):
    limit = get_settings().max_payload_bytes
    big = {"x": "a" * (limit + 10)}
    assert client.post("/v1/shares", json=big).status_code == 413


def test_delete_revokes(client):
    body, _ = _create(client)
    assert client.delete(f"/v1/shares/{body['token']}").status_code == 204
    assert client.get(f"/v1/shares/{body['token']}").status_code == 404
    # Deleting again is a 404.
    assert client.delete(f"/v1/shares/{body['token']}").status_code == 404


def test_memory_store_expiry():
    async def scenario():
        store = MemoryStore()
        record = await store.create({"n": "x"}, ttl_seconds=0)
        # ttl=0 → already expired; first get returns the (expired) record then drops it.
        fetched = await store.get(record.token)
        assert fetched is not None and fetched.is_expired
        assert await store.get(record.token) is None

    asyncio.run(scenario())
