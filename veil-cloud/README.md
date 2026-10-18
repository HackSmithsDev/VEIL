# VEIL Cloud

VEIL Cloud is an independently run FastAPI service for VEIL Guard accounts and
user-owned metadata. The desktop app reaches it over HTTPS; it is not bundled
into the desktop app and is not the local protection Engine.

**Data boundary:** Cloud stores account/profile details, program metadata, and
feedback. Do not send source code, confidential prompts, model responses, or
local Engine session secrets to this service.

## Current features

All application routes are under `/api/v1`:

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Create an account and return a bearer access token |
| `POST` | `/auth/login` | Authenticate and return a bearer access token |
| `GET` | `/auth/me` | Read the authenticated account |
| `POST` | `/auth/password-reset/request` | Request reset instructions by email |
| `POST` | `/auth/password-reset/confirm` | Consume a reset token and set a new password |
| `GET`, `PATCH` | `/profile` | Read or update the authenticated user's name |
| `GET`, `POST` | `/programs` | List or create the user's program metadata |
| `GET`, `PUT`, `DELETE` | `/programs/{program_id}` | Read, replace, or delete an owned program |
| `GET`, `POST` | `/feedback` | List or submit the authenticated user's feedback |
| `GET` | `/health` | Return a basic service health response |

Program records contain a name, version, platform, and optional purpose;
they are metadata, not source-code workspaces or a list of connected apps.
Feedback categories are `idea`, `issue`, `experience`, and `other`.
Authenticated routes enforce ownership in the service layer.

## Architecture

```text
main.py
  └── app.create_app()
      └── app/api/router.py → api/v1/routes.py
          ├── dependencies.py   bearer auth and database session
          ├── schemas.py        request/response validation
          └── app/services/     account, program, feedback, email

PostgreSQL ← SQLAlchemy models + Alembic migrations
Redis      ← expiring reset tokens and rate-limit counters
```

- `app/core/config.py` reads `VEIL_*` settings from the process environment or
  a local `.env`; `app/core/database.py` owns SQLAlchemy session setup.
- Passwords are hashed with `pwdlib`'s recommended Argon2 configuration.
  Access tokens are signed JWTs using HS256 and are short-lived. The UI keeps
  them in memory; there is no refresh-token API.
- PostgreSQL persists users, programs, and feedback. Schema changes belong in
  Alembic migrations under `alembic/versions/`.
- SMTP is optional for registration and feedback notifications. Email sending
  runs as FastAPI background work after the database record is committed.
- Redis is required for password-reset request rate limits and one-time reset
  tokens. The utility module also contains OTP/controller/model-state helpers;
  those are not a promise of a corresponding user-facing API or Engine
  integration.

## Configuration

Copy `.env.example` to `.env`, then set a unique `VEIL_JWT_SECRET` with at
least 32 characters. Never use an example value as a production secret.
Settings use the `VEIL_` prefix. Important groups:

- `VEIL_HOST`, `VEIL_PORT`, `VEIL_DEBUG`, `VEIL_ENVIRONMENT`
- `VEIL_DATABASE_URL`, `VEIL_REDIS_URL`
- `VEIL_JWT_SECRET`, `VEIL_ACCESS_TOKEN_MINUTES`
- `VEIL_CORS_ORIGINS` (comma-separated exact origins)
- `VEIL_SMTP_*` for optional mail, with exactly one of STARTTLS or implicit
  TLS enabled
- `VEIL_FEEDBACK_NOTIFICATION_EMAIL` for an optional team notification

Password-reset email requires SMTP and Redis. **Known configuration gap:**
the reset handlers currently read `password_reset_request_window_seconds`,
`password_reset_email_request_limit`, `password_reset_host_request_limit`,
and `password_reset_token_minutes` from `Settings`, but those fields are not
declared in `app/core/config.py`. The tests supply these values through mocks,
so reset behavior is not verified against normal application settings yet.
Declare and validate these settings before relying on password recovery.

## Run locally

Use PostgreSQL and Redis from the repository Compose file, then run the API
from this directory:

```bash
cd veil-cloud
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp -n .env.example .env
# Edit .env and set a unique VEIL_JWT_SECRET before startup.
docker compose -f ../docker-compose.yml up -d database cache
alembic upgrade head
python main.py
```

The API listens on `http://127.0.0.1:8089` by default. OpenAPI docs are at
`/docs`; the basic readiness route is `/api/v1/health`. To run the Cloud API in
Docker with migrations applied automatically, follow the root
[development instructions](../README.md).

`main.py` exposes the ASGI app as `main:app`. `app.create_app()` constructs the
FastAPI application and installs CORS middleware and versioned routes.

## Tests

```bash
cd veil-cloud
python -m pip install -r requirements-dev.txt
pytest
```

Tests cover account/profile flows, user-scoped program and feedback
operations, reset/email behavior with test doubles, and Redis utility
semantics. They do not replace an integration test against configured
PostgreSQL, Redis, or SMTP.

## Security and operational limits

- Keep authorization and ownership checks on the server; UI hiding is not
  access control.
- Never log passwords, bearer tokens, reset tokens, or feedback message bodies.
- Reset requests use a uniform response to reduce account enumeration; reset
  tokens are stored by digest and consumed once, subject to the configuration
  gap above.
- There is no email verification or access-token revocation/refresh flow.
  Existing access tokens remain valid until expiry, including after password
  changes.
- Health currently reports process-level status only; it does not verify
  PostgreSQL, Redis, or SMTP connectivity.
- This is an MVP API, not a public production deployment recipe. Production
  still needs deployment hardening, monitoring, backup/restore procedures,
  secret management, and verified reset configuration.
