# VEIL Guard Interface

The Interface is the React frontend packaged as the VEIL Guard desktop utility
by Tauri. It is the user's control surface; it does not install the Engine,
enforce security policy, or own cloud persistence.

## Included in the first UI slice

The current UI implements the account, profile, program-metadata, and feedback
flows against VEIL Cloud, with a protection-focused status and setup experience:

- **Protection** — local Engine and connector readiness with honest active,
  inactive, and unavailable states.
- **Setup** — explains the separate platform installer and optional local model
  setup. Installation itself is not implemented in this build.
- **Sign in / Create account** — optional; only required for VEIL Cloud
  profile, program metadata, and feedback features.
- **Programs** — list and search the user's program metadata; create, edit, and
  remove a record. AI-upgrade execution is not part of this initial slice.
- **Profile** — view and edit basic account details.
- **Feedback** — choose a category and submit a message. Tell users not to
  include credentials, source code, confidential prompts, or other secrets.
- **Account controls** — sign out from the account menu and view the app version.

Design every screen for loading, empty, validation, success, and recoverable
failure states. The setup page is informational only: this build does not
install the Engine, install Ollama, configure connectors, inspect prompts, or
block credential leaks. Do not present protection as active until the Engine
reports a verified status over authenticated local IPC.

## Component boundaries

```text
src/
  api/cloud/      VEIL Cloud HTTP client and resource calls
  components/layout/
                  App shell, navigation, and shared page framing
  hooks/          Cloud session and authentication state
  pages/          Auth, dashboard, programs, profile, and feedback
```

Keep network calls and response handling in the API layer, page composition in
`pages/`, and reusable presentation in `components/`. Add a state-management
library only when shared state becomes difficult to manage with React's built-in
tools.

## Desktop and cloud boundary

Tauri builds the frontend into a platform-specific desktop application. The
FastAPI cloud service remains separately deployed and is reached over HTTPS;
building the desktop executable does not bundle or deploy the backend.

Use Tauri's native capabilities only for desktop-specific needs. Keep cloud
authentication and authorization on the server, and do not rely on the client
to enforce ownership. The MVP keeps its short-lived access token in memory only:
restarting the app requires signing in again. Do not persist tokens to
`localStorage`; use a platform credential store if persistent sessions are
added later.

The Engine integration is a later phase and should use a deliberate local IPC
contract. Do not have the UI launch arbitrary shell commands or assume the
Engine is available. Local protection must remain usable without signing in;
Cloud-backed features should request authentication only when opened.

## Development

```bash
npm install
npm run dev
```

The UI uses `https://veil-api.hacksmiths.dev/api/v1` by default. For local
backend development, set `VITE_API_BASE_URL=http://127.0.0.1:8089/api/v1` in a
local Vite environment file. The normal desktop workflow is `npx tauri dev` or
`npx tauri build`. Both commands run Vite automatically: development serves
the UI to Tauri's WebView locally, and the production build embeds the generated
assets into the desktop bundle. No separate website is deployed.
`npm run build` alone only checks/builds the frontend assets and does not create
the desktop app.

On macOS Apple Silicon, `npx tauri build` creates
`src-tauri/target/release/bundle/macos/VEIL Guard.app` and a `.dmg` installer
under `src-tauri/target/release/bundle/dmg/`. Windows executables need a Windows
build host or CI runner.
