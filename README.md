# VEIL

VEIL is a local-first desktop security project with an optional cloud account
service. It is split into separately developed components: a React/Tauri
desktop interface, a Python Engine, a macOS installer, and the FastAPI Cloud
service.

> **Current protection status:** the desktop app, Cloud account/metadata
> features, and macOS installer are usable at their documented scope. The
> Engine is currently a Python library scaffold with contracts, an
> experimental credential-pattern policy, and routing tests. It does not
> capture prompts from other applications, connect to Ollama, or run as a
> background service. VEIL Guard does **not** currently inspect prompts or
> prevent credential leaks.

## Project layout

```text
.
├── veil-cloud/             FastAPI API, PostgreSQL models/migrations, Redis use
├── veil-guard/
│   ├── interface/          React frontend and Tauri desktop application
│   ├── engine/             Local policy/routing library and its tests
│   └── installer/          Qt Installer Framework macOS package
├── docker-compose.yml      Local PostgreSQL, Redis, Cloud API, optional tunnel
└── .env.example            Root Cloudflare Tunnel token template
```

Each component README describes its boundaries, setup, tests, and incomplete
work: [Cloud](./veil-cloud/README.md),
[Interface](./veil-guard/interface/README.md),
[Engine](./veil-guard/engine/README.md), and
[Installer](./veil-guard/installer/README.md).

## Architecture and data boundaries

```text
React + Tauri desktop app ── HTTPS ──► VEIL Cloud API
           │                              │
           │ future authenticated IPC     ├── PostgreSQL: accounts, program
           ▼                              │   metadata, feedback
    VEIL Guard Engine                     └── Redis: expiring/runtime state
    (not integrated yet)
```

- **Interface** presents the desktop UI, stores local Ollama preferences, and
  calls Cloud endpoints for account, profile, program metadata, and feedback.
- **Cloud** authenticates users and owns server-side validation, user-scoped
  authorization, persistence, and optional email delivery. It must not receive
  confidential prompts, source code, local model responses, or Engine session
  secrets.
- **Engine** is intended to assess each request locally and route confidential
  work to a local processor. Its current protocols and experimental pattern
  policy are not production protection.
- **Installer** packages the desktop app for macOS only. It does not install an
  Engine service or enable protection.

Cloud sign-in is optional. The desktop access token is held in memory and is
discarded when the app exits or the user signs out. Do not persist it in
`localStorage`. Cloud-owned records remain server-side; uninstalling the
desktop app does not delete those records.

## Local development

### Start the Cloud API and its dependencies

From the repository root, create `veil-cloud/.env` from its example and replace
the development JWT secret with a unique random value of at least 32
characters. The root `.env` and Cloud `.env` contain local credentials and must
not be committed.

```bash
cp -n veil-cloud/.env.example veil-cloud/.env
# Edit veil-cloud/.env and set a unique VEIL_JWT_SECRET.
docker compose up --build database cache cloud
```

The command starts PostgreSQL, Redis, and the API on
`http://127.0.0.1:8089`; the Cloud container applies Alembic migrations before
starting. API documentation is at `http://127.0.0.1:8089/docs`, and readiness
is exposed at `/api/v1/health`. The named-service command deliberately leaves
the Cloudflare Tunnel out of local development. To run that optional tunnel,
configure its token in the root `.env` using [.env.example](./.env.example).
Compose passes it to the `cloudflared` container as `TUNNEL_TOKEN`, which the
container uses to run the tunnel.

To run the API directly on the host instead, start only its dependencies and
run the Cloud instructions in [veil-cloud/README.md](./veil-cloud/README.md).

### Start the desktop app

In another terminal:

```bash
cd veil-guard/interface
npm install
npx tauri dev
```

The interface uses `VITE_API_BASE_URL` to locate Cloud. Create or update a local
`.env.development` from
[`.env.example`](./veil-guard/interface/.env.example) if the local API URL
differs from the configured default. Local `.env.development` and
`.env.production` files are ignored by Git. The normal desktop workflow is
`npx tauri dev` / `npx tauri build`; building the interface alone does not
produce the desktop app.

## Tests and builds

Run component checks from each component directory:

```bash
# Cloud API and Redis behavior
cd veil-cloud
python3 -m pip install -r requirements-dev.txt
pytest

# Interface
cd ../veil-guard/interface
npm install
npm run lint
npm run build

# Engine
cd ../engine
python3 -m pip install -e ".[test]"
pytest -v

# Installer script tests (standard library)
cd ../installer
python3 -m unittest discover -s native/tests -v
```

Build the desktop app with `npx tauri build` from `veil-guard/interface`.
Creating the macOS Qt Installer Framework package is a separate operation;
see the [Installer README](./veil-guard/installer/README.md). Windows and Linux
desktop/installer packages are not currently configured.

## Security and contributor notes

- Never commit `.env` files, tokens, signing keys, or real credentials. Use the
  checked-in `.env.example` files only as templates.
- Keep confidential content local. Do not add prompt bodies, secrets, or model
  responses to Cloud requests or logs.
- Server-side authorization is authoritative; client-side visibility is not
  an access-control boundary.
- Do not advertise protection as active until a supported connector, policy,
  local processor, authenticated IPC, and installed Engine report verified
  readiness.
- Keep changes within the component that owns the behavior and update that
  component's README when its setup, contract, or status changes.
