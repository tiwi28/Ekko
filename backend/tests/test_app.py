"""Smoke tests that don't need a database.

TestClient(app) without a `with` block skips the lifespan, so no pool is opened.
"""

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.security import create_access_token, decode_access_token, hash_password, verify_password

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_cron_endpoint_rejects_missing_secret():
    assert client.post("/digest/run").status_code == 401
    assert client.post("/digest/run", headers={"X-Cron-Secret": "wrong"}).status_code == 401


def test_protected_route_requires_token():
    assert client.get("/tasks").status_code == 401


def test_password_roundtrip():
    stored = hash_password("hunter22")
    assert verify_password("hunter22", stored)
    assert not verify_password("wrong", stored)


def test_jwt_roundtrip():
    settings = get_settings()
    assert decode_access_token(create_access_token(42, settings), settings) == 42
