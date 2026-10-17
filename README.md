# VEIL

VEIL Guard is a desktop utility with a separate local Engine, native installer,
and optional Cloud account features. The utility is built with React and
packaged with Tauri; VEIL Cloud is a separate FastAPI application.

## Components

```text
┌────────────────────────────────┐          ┌───────────────────────────────┐
│ VEIL Guard desktop utility     │  HTTPS   │ VEIL Cloud (optional features)│
│                                ├─────────►│ FastAPI                       │
│ React UI + Tauri host          │          │ Accounts, profiles, programs, │
│                                │          │ feedback                      │
└───────────────┬────────────────┘          └───────────────────────────────┘
                │
                │ authenticated local IPC (future)
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

The Engine handles future local prompt assessment and processing. The separate
platform installer sets up the utility and Engine; it does not require Cloud
sign-in. The installed utility should manage protection locally, while sign-in
is optional for Cloud profile, program metadata, and feedback features.

## Initial delivery scope

The Cloud-backed features are:

- Sign up, sign in, sign out, and view/update the signed-in user's profile.
- Create, list, view, update, and delete a user's program metadata.
- Submit and view feedback associated with the signed-in user.
- Show loading, empty, validation, success, and recoverable error states.
- Keep each user's records scoped to that user on the server.

The initial program record is metadata only: name, version, platform, and an
optional short purpose. Do not accept or upload source code as part of this
slice.

## UI outline

1. **Protection** — local Engine/connector readiness and protection status;
   this must be usable without a Cloud account.
2. **Setup** — installer status, optional local processing, and connectors.
3. **Programs** — searchable/list view and add/edit details form. Treat these
   as optional Cloud metadata records, not protected source-code workspaces.
4. **Account** — optional sign-in and profile management for Cloud features.
5. **Feedback** — optional Cloud feature; warn users
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
- **Installer** owns platform-specific installation, background service setup,
  consent, upgrades, repair, and uninstall. It must not depend on VEIL Cloud.
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
  installer/                Separate Windows, macOS, and Linux installer work
docker-compose.yml          Local PostgreSQL + cloud API development stack
```

Each component has its own README with responsibilities and status. The
Cloud-backed account/program/feedback slice is implemented. The macOS Qt
Installer Framework project stages the desktop app for packaging, but the
framework build tool is not installed and no installer binary has been
generated. The Engine runtime and Windows/Linux installers are not ready, so
VEIL Guard does not provide active prompt protection yet.

## Run locally

Configure a random `VEIL_JWT_SECRET` in `veil-cloud/.env` and set
`CLOUDFLARED_TUNNEL_TOKEN` in the root `.env` to the tunnel token from the
Cloudflare dashboard. Create either file from its `.env.example` if needed.
Keep both real values private. The Cloudflared container uses the checked-in,
non-secret `cloudflared/config.yml` ingress mapping to route
`veil-api.hacksmiths.dev` to the `cloud` service on port 8089. Never put the
tunnel token in that config file or commit it.

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
