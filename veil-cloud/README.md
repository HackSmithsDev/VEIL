# VEIL Cloud

VEIL Cloud is the separately deployed FastAPI service used by the VEIL Guard
desktop application. The initial scope is account authentication and
user-scoped storage for profile details, non-confidential program metadata, and
feedback.

It is not the local security engine. Do not send source code, confidential
prompts, model responses, or session secrets to this service as part of the
initial feature slice.

## Responsibilities

- Authenticate users and enforce ownership on every user-specific operation.
- Validate requests and responses at the API boundary.
- Persist account/profile, program metadata, and feedback records.
- Manage database configuration and schema changes through SQLAlchemy and
  Alembic.
- Return consistent HTTP errors without exposing internal details.

## Suggested application boundaries

```text
app/
  __init__.py        create_app() application factory
  api/v1/            Versioned routes, request schemas, auth dependencies
  core/              Settings, database/session setup, auth, errors
  db/models/         SQLAlchemy persistence models
  services/          Account, program, and feedback operations
tests/               API integration tests
alembic/versions/    Version-controlled database migrations
```

Keep HTTP handling in the API layer and account/program/feedback operations in
services. Services use SQLAlchemy sessions and models directly for this small
MVP; add repositories only if query complexity justifies them. PostgreSQL stores
persistent relational records; Redis stores short-lived and shared runtime state.

## Initial API resources

Define and version the API under `/api/v1`. The first UI flow needs:

- Authentication: create an account, sign in, and retrieve the current
  account. The desktop client keeps the short-lived access token in memory and
  discards it on sign out; it is not persisted to local storage.
- Profile: retrieve and update the current user's basic profile.
- Programs: list and manage only the current user's metadata records.
- Feedback: submit feedback and, if needed by the product, retrieve the user's
  submissions.
- Health: a minimal service readiness endpoint for deployment checks.
- Email: send a welcome message at registration, a feedback receipt to the
  submitter, and an optional feedback notification to the configured team inbox.
- Redis-backed runtime state: short-lived OTP/reset codes (10-minute default),
  refresh tokens, connection state, and active controller/model tracking.

The initial program fields are name, version, platform, and optional purpose.
Feedback accepts one of four categories and a bounded message.

## Data and security rules

- Store only fields needed for the initial user/profile, program metadata, and
  feedback workflows.
- Hash passwords with a purpose-built password hashing algorithm; never store
  plaintext passwords.
- Enforce ownership in the service/API layer, not only in UI filtering.
- Validate all inputs server-side and bound text sizes.
- Do not log passwords, tokens, or feedback message bodies.
- Keep database credentials and signing keys out of source control; configure
  them through the runtime environment.
- Configure SMTP with `VEIL_SMTP_*`; delivery is optional locally and uses
  STARTTLS on port 587 or implicit TLS on port 465 by default configuration.
- Emails run after the API response in FastAPI background tasks. Delivery
  failures are logged without undoing an already-persisted account or feedback
  record.
- Do not treat feedback or program metadata as safe to publish. Limit access to
  the owning user and authorized service operators.

## Database and migrations

PostgreSQL is the persistent database. Alembic owns its relational schema
changes; the initial migration creates users, programs, and feedback.
Redis is a separate key-value service for expiring codes and runtime state; it
does not use Alembic migrations.

## Local development

Install dependencies into your global Python environment (no project virtual
environment) and configure `VEIL_JWT_SECRET` with at least 32 random
characters. The `.env` configures local PostgreSQL and Redis at
`127.0.0.1`; the root Compose stack starts both services and overrides their
addresses for the Cloud container.

```bash
cd veil-cloud
python3 -m pip install --user -r requirements-dev.txt
cp -n .env.example .env
# Replace VEIL_JWT_SECRET in .env with a random secret before starting.
docker compose -f ../docker-compose.yml up -d database cache
alembic upgrade head
python3 main.py
```

Start the PostgreSQL and Redis services before running the API directly from
the host. Alternatively, run `docker compose up --build` from the repository
root to start the full stack and apply Alembic migrations automatically.

`app.create_app()` assembles the FastAPI application. `main.py` is the local
Uvicorn entry point and exposes `app` for ASGI servers.

API documentation is served at `http://127.0.0.1:8089/docs`. Run tests with
`pytest`. `docker compose up --build` from the repository root starts the
PostgreSQL-backed API after configuring `veil-cloud/.env`.

This is an MVP, not a production-hardened identity service: it has short-lived
bearer tokens but no refresh-token flow, password reset, email verification, or
rate limiting yet. Redis OTP storage is available for a future password-reset
flow, but those API endpoints are not implemented yet. Welcome and feedback
emails are notifications, not proof of verified email ownership.