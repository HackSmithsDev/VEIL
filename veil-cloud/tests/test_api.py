from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.api.v1 import routes
from app.core.config import Settings
from app.core.database import get_db
from app.db.base import Base
from app.db import models  # noqa: F401
from main import app
from app.services.email import client as email_client
from app.services.email.templates import render_feedback_notification

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


def test_app_factory_creates_cloud_application() -> None:
    application = create_app()
    assert application.title == "VEIL Cloud API"
    with TestClient(application) as test_client:
        assert test_client.get("/api/v1/health").json() == {"status": "ok"}


def test_example_jwt_secret_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(
            jwt_secret="replace-this-with-a-random-secret-of-at-least-32-characters"
        )


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    Base.metadata.create_all(test_engine)

    def override_get_db() -> Iterator[Session]:
        database = TestSession()
        try:
            yield database
        finally:
            database.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(routes, "send_welcome_email", lambda recipient, full_name: None)
    monkeypatch.setattr(
        routes,
        "send_feedback_emails",
        lambda user_email, full_name, category, feedback_message: None,
    )
    monkeypatch.setattr(
        routes,
        "send_password_reset_email",
        lambda recipient, full_name, reset_token, expiration_minutes: None,
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine)


def register(client: TestClient, email: str = "ada@example.com") -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Ada Lovelace",
            "password": "correct-horse-battery-staple",
        },
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_register_login_and_profile(client: TestClient) -> None:
    headers = register(client)
    profile = client.get("/api/v1/profile", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["email"] == "ada@example.com"
    assert "password" not in profile.json()
    assert "password_hash" not in profile.json()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "ADA@example.com", "password": "correct-horse-battery-staple"},
    )
    assert login.status_code == 200

    update = client.patch(
        "/api/v1/profile",
        headers=headers,
        json={"full_name": "Ada Byron"},
    )
    assert update.status_code == 200
    assert update.json()["full_name"] == "Ada Byron"


def test_authentication_and_duplicate_registration(client: TestClient) -> None:
    headers = register(client)
    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "email": "ADA@example.com",
            "full_name": "Ada",
            "password": "correct-horse-battery-staple",
        },
    )
    assert duplicate.status_code == 409
    assert client.get("/api/v1/profile").status_code == 401
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "wrong-password"},
    )
    assert bad_login.status_code == 401
    assert client.get("/api/v1/profile", headers={"Authorization": "Bearer invalid"}).status_code == 401
    assert headers["Authorization"].startswith("Bearer ")


def test_password_reset_request_and_confirmation(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    register(client)
    token_store: dict[str, str] = {}
    rate_limits: dict[str, int] = {}
    sent: list[tuple[str, str, str, int]] = []

    async def increment_rate_limit(key: str, _expire_seconds: int) -> int:
        rate_limits[key] = rate_limits.get(key, 0) + 1
        return rate_limits[key]

    async def set_password_reset_token(
        token_digest: str,
        email: str,
        _expire_seconds: int,
    ) -> None:
        token_store[token_digest] = email

    async def consume_password_reset_token(token_digest: str) -> str | None:
        return token_store.pop(token_digest, None)

    monkeypatch.setattr(
        routes,
        "settings",
        type(
            "ResetSettings",
            (),
            {
                "email_enabled": True,
                "password_reset_request_window_seconds": 3600,
                "password_reset_email_request_limit": 5,
                "password_reset_host_request_limit": 50,
                "password_reset_token_minutes": 30,
            },
        )(),
    )
    monkeypatch.setattr(routes, "increment_rate_limit", increment_rate_limit)
    monkeypatch.setattr(routes, "set_password_reset_token", set_password_reset_token)
    monkeypatch.setattr(
        routes,
        "consume_password_reset_token",
        consume_password_reset_token,
    )
    monkeypatch.setattr(
        routes,
        "send_password_reset_email",
        lambda recipient, full_name, reset_token, expiration_minutes: sent.append(
            (recipient, full_name, reset_token, expiration_minutes)
        ),
    )

    request = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "ada@example.com"},
    )
    unknown_request = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "unknown@example.com"},
    )
    assert request.status_code == 202
    assert request.json() == unknown_request.json()
    assert len(sent) == 1
    recipient, _full_name, reset_token, expiration_minutes = sent[0]
    assert recipient == "ada@example.com"
    assert expiration_minutes == 30
    assert len(token_store) == 2

    confirmation = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "email": "ada@example.com",
            "reset_token": reset_token,
            "new_password": "a-new-correct-horse-battery",
        },
    )
    assert confirmation.status_code == 200
    assert client.post(
        "/api/v1/auth/login",
        json={
            "email": "ada@example.com",
            "password": "a-new-correct-horse-battery",
        },
    ).status_code == 200
    assert client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "email": "ada@example.com",
            "reset_token": reset_token,
            "new_password": "another-new-correct-horse-battery",
        },
    ).status_code == 400


def test_password_reset_is_unavailable_without_email_delivery(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        routes,
        "settings",
        type("ResetSettings", (), {"email_enabled": False})(),
    )

    response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "ada@example.com"},
    )

    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_password_reset_requests_are_rate_limited_per_email(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counts: dict[str, int] = {}
    tokens: list[tuple[str, str, int]] = []

    async def increment_rate_limit(key: str, _expire_seconds: int) -> int:
        counts[key] = counts.get(key, 0) + 1
        return counts[key]

    async def set_password_reset_token(
        token_digest: str,
        email: str,
        expire_seconds: int,
    ) -> None:
        tokens.append((token_digest, email, expire_seconds))

    monkeypatch.setattr(
        routes,
        "settings",
        type(
            "ResetSettings",
            (),
            {
                "email_enabled": True,
                "password_reset_request_window_seconds": 3600,
                "password_reset_email_request_limit": 1,
                "password_reset_host_request_limit": 50,
                "password_reset_token_minutes": 30,
            },
        )(),
    )
    monkeypatch.setattr(routes, "increment_rate_limit", increment_rate_limit)
    monkeypatch.setattr(routes, "set_password_reset_token", set_password_reset_token)

    payload = {"email": "unknown@example.com"}
    assert client.post("/api/v1/auth/password-reset/request", json=payload).status_code == 202
    limited = client.post("/api/v1/auth/password-reset/request", json=payload)

    assert limited.status_code == 429
    assert len(tokens) == 1


def test_programs_are_user_scoped_and_crud_works(client: TestClient) -> None:
    owner_headers = register(client)
    other_headers = register(client, "grace@example.com")
    create = client.post(
        "/api/v1/programs",
        headers=owner_headers,
        json={
            "name": "Compiler",
            "version": "1.2",
            "platform": "macOS",
            "purpose": "Code analysis",
        },
    )
    assert create.status_code == 201
    program_id = create.json()["id"]
    assert client.get("/api/v1/programs", headers=other_headers).json() == []
    assert client.get(f"/api/v1/programs/{program_id}", headers=other_headers).status_code == 404

    update = client.put(
        f"/api/v1/programs/{program_id}",
        headers=owner_headers,
        json={"name": "Compiler", "version": "2.0", "platform": "macOS"},
    )
    assert update.status_code == 200
    assert update.json()["purpose"] is None
    assert client.delete(f"/api/v1/programs/{program_id}", headers=owner_headers).status_code == 204
    assert client.get(f"/api/v1/programs/{program_id}", headers=owner_headers).status_code == 404


def test_feedback_is_scoped_to_authenticated_user(client: TestClient) -> None:
    owner_headers = register(client)
    other_headers = register(client, "grace@example.com")
    create = client.post(
        "/api/v1/feedback",
        headers=owner_headers,
        json={"category": "idea", "message": "Please add a safer update preview."},
    )
    assert create.status_code == 201
    assert len(client.get("/api/v1/feedback", headers=owner_headers).json()) == 1
    assert client.get("/api/v1/feedback", headers=other_headers).json() == []
    assert client.post(
        "/api/v1/feedback",
        headers=owner_headers,
        json={"category": "idea", "message": "short"},
    ).status_code == 422


def test_registration_and_feedback_schedule_email_tasks(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scheduled: list[tuple[str, tuple[str, ...]]] = []
    monkeypatch.setattr(
        routes,
        "send_welcome_email",
        lambda recipient, full_name: scheduled.append(
            ("welcome", (recipient, full_name))
        ),
    )
    monkeypatch.setattr(
        routes,
        "send_feedback_emails",
        lambda user_email, full_name, category, feedback_message: scheduled.append(
            ("feedback", (user_email, full_name, category, feedback_message))
        ),
    )

    headers = register(client)
    response = client.post(
        "/api/v1/feedback",
        headers=headers,
        json={"category": "idea", "message": "Please add a preview."},
    )

    assert response.status_code == 201
    assert scheduled == [
        ("welcome", ("ada@example.com", "Ada Lovelace")),
        ("feedback", ("ada@example.com", "Ada Lovelace", "idea", "Please add a preview.")),
    ]


def test_feedback_email_template_escapes_user_content() -> None:
    _, text, html = render_feedback_notification(
        "Ada <Admin>",
        "ada@example.com",
        "idea",
        "<script>alert('x')</script>",
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "<script>" in text


def test_smtp_client_uses_starttls_and_authentication(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSmtp:
        started_tls = False
        authenticated = False
        sent_message = False

        def __enter__(self) -> "FakeSmtp":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def starttls(self, context: object) -> None:
            self.started_tls = True

        def login(self, username: str, password: str) -> None:
            self.authenticated = username == "smtp-user" and password == "smtp-pass"

        def send_message(self, message: object) -> None:
            self.sent_message = True

    fake_smtp = FakeSmtp()
    monkeypatch.setattr(email_client.settings, "smtp_host", "smtp.example.test")
    monkeypatch.setattr(email_client.settings, "smtp_port", 587)
    monkeypatch.setattr(email_client.settings, "smtp_username", "smtp-user")
    monkeypatch.setattr(email_client.settings, "smtp_password", SecretStr("smtp-pass"))
    monkeypatch.setattr(email_client.settings, "smtp_from_email", "sender@example.test")
    monkeypatch.setattr(email_client.settings, "smtp_starttls", True)
    monkeypatch.setattr(email_client.settings, "smtp_ssl_tls", False)
    monkeypatch.setattr(email_client.settings, "email_enabled", True)
    monkeypatch.setattr(email_client.smtplib, "SMTP", lambda *args, **kwargs: fake_smtp)

    email_client.send_message(
        email_client.build_message(
            "recipient@example.test",
            "Test message",
            "Plain text",
            "<p>HTML</p>",
        )
    )

    assert fake_smtp.started_tls
    assert fake_smtp.authenticated
    assert fake_smtp.sent_message


def test_smtp_ssl_client_receives_tls_context(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSmtp:
        received_context = False

        def __enter__(self) -> "FakeSmtp":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def login(self, username: str, password: str) -> None:
            return None

        def send_message(self, message: object) -> None:
            return None

    fake_smtp = FakeSmtp()

    def create_ssl_client(*args: object, **kwargs: object) -> FakeSmtp:
        fake_smtp.received_context = kwargs.get("context") is not None
        return fake_smtp

    monkeypatch.setattr(email_client.settings, "smtp_host", "smtp.example.test")
    monkeypatch.setattr(email_client.settings, "smtp_port", 465)
    monkeypatch.setattr(email_client.settings, "smtp_from_email", "sender@example.test")
    monkeypatch.setattr(email_client.settings, "smtp_starttls", False)
    monkeypatch.setattr(email_client.settings, "smtp_ssl_tls", True)
    monkeypatch.setattr(email_client.settings, "email_enabled", True)
    monkeypatch.setattr(email_client.smtplib, "SMTP_SSL", create_ssl_client)

    email_client.send_message(
        email_client.build_message(
            "recipient@example.test",
            "Test message",
            "Plain text",
            "<p>HTML</p>",
        )
    )

    assert fake_smtp.received_context
