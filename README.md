# VEIL

VEIL is a desktop product with a cloud account service. The desktop interface is
built with React and packaged with Tauri; the cloud service is a separate
FastAPI application.

## Components

```text
┌────────────────────────────────┐          ┌───────────────────────────────┐
│ VEIL Guard desktop application │  HTTPS   │ VEIL Cloud                    │
│                                ├─────────►│ FastAPI                       │
│ React UI + Tauri host          │          │ Accounts, profiles, programs, │
│                                │          │ feedback                      │
└───────────────┬────────────────┘          └───────────────────────────────┘
                │
                │ local interface (later phase)
                ▼
┌────────────────────────────────┐
│ VEIL Guard Engine               │
│ Local protected processing      │
└────────────────────────────────┘
```

The cloud service stores account/profile details, non-confidential program
metadata used for future AI-upgrade features, and user feedback. It is not the
confidential processing engine. Source code, prompts, model responses, and
session secrets are out of scope for this initial cloud feature set.

The Engine is a separate local-runtime project. Its security, sandbox, DLP, and
local-AI workflows are not prerequisites for building the initial account,
program-metadata, and feedback experience.

## Initial delivery scope

The first vertical slice is the desktop UI plus cloud API:

- Sign up, sign in, sign out, and view/update the signed-in user's profile.
- Create, list, view, update, and delete a user's program metadata.
- Submit and view feedback associated with the signed-in user.
- Show loading, empty, validation, success, and recoverable error states.
- Keep each user's records scoped to that user on the server.

The initial program record is metadata only: name, version, platform, and an
optional short purpose. Do not accept or upload source code as part of this
slice.

## UI outline

1. **Authentication** — sign-in and account-creation screens.
2. **Dashboard** — a concise welcome, program and feedback counts, and clear
   links to the main actions.
3. **Programs** — searchable/list view and add/edit details form. Treat these
   as metadata records, not protected source-code workspaces.
4. **Profile** — view and edit basic account details.
5. **Feedback** — category and message; warn users
   not to include passwords, source code, prompts, or other secrets.
6. **Settings** — account details and application version; avoid implying
   local Engine security controls are active until implemented.

## Boundaries and data flow

- **Interface** owns presentation, input validation for usability, and calls to
  the cloud API. Server-side validation remains authoritative.
- **Cloud** owns authentication, authorization, validation, persistence, and
  user-scoped access to profile, program, and feedback records.
- **Engine** will own future local confidential processing. It must not be
  represented as implemented merely because its directory exists.
- Tauri packages the desktop interface as a platform application. The cloud
  backend is deployed separately and is not bundled into that desktop app.

Never store plaintext passwords. Do not log credentials, access tokens, or
submitted feedback bodies. Keep secrets out of source control and use
environment-based configuration for local development and deployment.

## Repository layout

```text
veil-cloud/                 FastAPI cloud service and Alembic migrations
veil-guard/
  interface/                React UI and Tauri desktop host
  engine/                   Separate local security/runtime project
docker-compose.yml          Local PostgreSQL + cloud API development stack
```

Each component has its own README with its responsibilities and development
entry points. The first account/program/feedback slice is now implemented; the
Engine remains unimplemented and is intentionally out of scope.

## Run locally

Configure a random `VEIL_JWT_SECRET` in `veil-cloud/.env` and set
`CLOUDFLARED_TUNNEL_TOKEN` in the root `.env` to the tunnel token from the
Cloudflare dashboard. Create either file from its `.env.example` if needed.
Keep both real values private. The Cloudflared container connects to the
`cloud` service; configure the dashboard's tunnel origin as
`http://cloud:8089`.

```bash
cp -n .env.example .env
cp -n veil-cloud/.env.example veil-cloud/.env
# Edit both env files and replace the placeholders with real values.
docker compose up --build
```

In another terminal, start the desktop application:

```bash
cd veil-guard/interface
npm install
npx tauri dev
```

Tauri builds a native bundle for the build host. Producing a Windows executable
requires a Windows build environment or a suitable Windows CI runner.
