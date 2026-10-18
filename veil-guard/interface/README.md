# VEIL Guard Interface

The Interface is the React frontend hosted in a Tauri desktop application. It
is the user's control surface; it does not install or run the Engine, inspect
prompts, enforce security policy, or own Cloud persistence.

## Current screens and behavior

- **Protection** reports the Engine as disconnected and protection as off.
  This build does not inspect AI requests or block credential leaks.
- **Setup** explains the missing Engine, local processor, and connector
  integrations. It is informational; no setup steps install those components.
- **Settings** saves an Ollama loopback URL and optional preferred model name
  in this device's `localStorage`. These are preferences only: the app does
  not connect to Ollama or download/use a model.
- **Account** offers optional VEIL Cloud sign-in and account creation.
- **Profile** reads and updates the signed-in user's display name. Email
  changes are not supported.
- **Program Catalog** manages the user's Cloud program metadata; it does not
  discover installed, connected, or protected applications.
- **Feedback** submits and lists feedback associated with the signed-in
  account. Do not include credentials, source code, or confidential prompts.
- **Uninstall** launches the Qt Installer Framework maintenance tool from an
  installed macOS application. It does not delete Cloud records or local
  preferences.

Cloud credentials are held in React memory and are lost when the app exits.
They are not stored in `localStorage`. Cloud access is optional and is not a
prerequisite for local app screens.

## Source layout

```text
src/
  api/cloud/       HTTP client for VEIL Cloud
  components/      Shared dialog and app-shell UI
  hooks/           In-memory Cloud session/authentication state
  pages/           Protection, setup, settings, account, profile,
                   program catalog, and feedback screens
  App.jsx          Navigation and optional Cloud access gates
src-tauri/
  src/             Native Tauri host and macOS maintenance-tool command
  capabilities/    Tauri capability/permission declarations
  tauri.conf.json  Desktop identity, window, CSP, and build commands
```

Keep HTTP request/response handling in the API layer, page composition in
`pages/`, and reusable presentation in `components/`. Server authorization is
authoritative; UI state and visibility are never access controls.

## Run and build

Requirements: Node.js/npm and the Rust toolchain required by Tauri 2. From this
directory:

```bash
npm install
npx tauri dev
```

Vite serves the UI on `http://127.0.0.1:5176`; the desktop dev command starts it
automatically. Start the VEIL Cloud API separately if you want to use
Cloud-backed features; see [the Cloud README](../../veil-cloud/README.md).

The Cloud API base URL is injected at build time through
`VITE_API_BASE_URL`. Vite loads `.env.development` in development and
`.env.production` for production builds. These local mode files are ignored by
Git; `.env.example` is a template and is not loaded directly. The default
development URL is `http://127.0.0.1:8089/api/v1`; for another target, set the
variable in the appropriate local mode file or build environment. Remote URLs
must use HTTPS; HTTP is accepted only for loopback hosts. Do not put credentials
or tokens in the URL.

```bash
npm run lint
npm run build
npx tauri build
```

`npm run build` builds frontend assets only. `npx tauri build` builds a native
desktop bundle for the current host; creating the separate macOS setup wizard
is documented in [the Installer README](../installer/README.md). Windows
artifacts require a Windows build host or CI runner.

## Desktop/cloud boundary

The Cloud service is separately deployed and reached over HTTPS. Tauri does
not bundle or deploy it. The current Tauri command is limited to launching the
macOS maintenance tool for uninstall; it is not Engine IPC and does not launch
arbitrary shell commands. A future Engine connection must use a designed,
authenticated local IPC contract and report verified readiness before the UI
can show protection as active.

The default window opens at 620 × 440 and is resizable. The Content Security
Policy and Tauri capabilities live in `src-tauri/tauri.conf.json` and
`src-tauri/capabilities/`; review them when adding native or network access.

## Known limits

- There is no frontend automated-test script or test suite configured yet.
- There is no router/state-management dependency; app navigation and session
  state use React state/hooks.
- Local Ollama settings do not connect to Ollama.
- Protection is not implemented, and there is no Engine service, app
  connector, or Interface-to-Engine IPC.
- macOS uninstall is available only for an installed app in an Applications
  directory with the expected bundle identity and installer maintenance tool.
