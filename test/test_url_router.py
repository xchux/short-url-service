from datetime import datetime, timedelta

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Helper for expiration date
now = datetime.now()
future_exp = (now + timedelta(days=30)).isoformat()
past_exp = (now - timedelta(days=1)).isoformat()


@pytest.fixture(autouse=True)
def disable_rate_limit(monkeypatch):
    # Patch redis_client methods to avoid rate limiting
    monkeypatch.setattr(
        "app.middleware.rate_limit.redis_client.hexists", lambda *a, **kw: False
    )
    monkeypatch.setattr(
        "app.middleware.rate_limit.redis_client.get", lambda *a, **kw: None
    )
    monkeypatch.setattr(
        "app.middleware.rate_limit.redis_client.set", lambda *a, **kw: None
    )
    monkeypatch.setattr(
        "app.middleware.rate_limit.redis_client.incr", lambda *a, **kw: None
    )
    monkeypatch.setattr(
        "app.middleware.rate_limit.redis_client.hset", lambda *a, **kw: None
    )
    yield


def test_create_short_url_new(monkeypatch):
    monkeypatch.setattr(
        "app.api.routers.url_router.get_pw_url_by_original", lambda url: None
    )
    monkeypatch.setattr(
        "app.api.routers.url_router.generate_short_code", lambda: "abc123"
    )
    monkeypatch.setattr("app.api.routers.url_router.get_pw_url", lambda code: None)
    monkeypatch.setattr(
        "app.api.routers.url_router.save_url", lambda code, url, exp: None
    )
    resp = client.post("/api/shorten", json={"original_url": "https://example.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["short_url"].endswith("/api/abc123")
    assert data["expiration_date"] is not None


def test_create_short_url_existing(monkeypatch):
    # Simulate existing URL
    class PwUrl:
        short_code = "exist1"

    monkeypatch.setattr(
        "app.api.routers.url_router.get_pw_url_by_original", lambda url: PwUrl()
    )
    monkeypatch.setattr(
        "app.api.routers.url_router.update_expiration_date", lambda code, exp: None
    )
    resp = client.post("/api/shorten", json={"original_url": "https://exist.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["short_url"].endswith("/api/exist1")
    assert data["expiration_date"] is not None


def test_create_short_url_invalid_url():
    resp = client.post("/api/shorten", json={"original_url": "not-a-url"})
    assert resp.status_code == 422  # Pydantic validation error


def test_create_short_url_cannot_generate(monkeypatch):
    # Simulate all codes taken
    monkeypatch.setattr(
        "app.api.routers.url_router.get_pw_url_by_original", lambda url: None
    )
    monkeypatch.setattr(
        "app.api.routers.url_router.generate_short_code", lambda: "taken1"
    )
    monkeypatch.setattr("app.api.routers.url_router.get_pw_url", lambda code: True)
    resp = client.post("/api/shorten", json={"original_url": "https://fail.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert data["reason"] == "Could not generate unique short code"


def test_create_short_url_db_error(monkeypatch):
    monkeypatch.setattr(
        "app.api.routers.url_router.get_pw_url_by_original", lambda url: None
    )
    monkeypatch.setattr(
        "app.api.routers.url_router.generate_short_code", lambda: "err123"
    )
    monkeypatch.setattr("app.api.routers.url_router.get_pw_url", lambda code: None)

    def raise_exc(*a, **kw):
        raise Exception("db error")

    monkeypatch.setattr("app.api.routers.url_router.save_url", raise_exc)
    resp = client.post("/api/shorten", json={"original_url": "https://err.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert data["reason"] == "Database error"


def test_redirect_short_url_success(monkeypatch):
    class PwUrl:
        original_url = "https://redirect.com"
        expiration_date = now + timedelta(days=30)

    monkeypatch.setattr(
        "app.api.routers.url_router.get_pw_url",
        lambda code: PwUrl(),
    )
    resp = client.get("/api/abc123", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://redirect.com"


def test_redirect_short_url_not_found(monkeypatch):
    monkeypatch.setattr("app.api.routers.url_router.get_pw_url", lambda code: None)
    resp = client.get("/api/notfound")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Short URL not found"


def test_redirect_short_url_expired(monkeypatch):
    class PwUrl:
        original_url = "https://expired.com"
        expiration_date = now - timedelta(days=1)

    monkeypatch.setattr("app.api.routers.url_router.get_pw_url", lambda code: PwUrl())
    resp = client.get("/api/expired")
    assert resp.status_code == 410
    assert resp.json()["detail"] == "Short URL expired"
