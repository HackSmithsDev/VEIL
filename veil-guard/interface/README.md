# VEIL Guard Interface

The Interface is the React frontend packaged as the VEIL Guard desktop utility
by Tauri. It is the user's control surface; it does not install the Engine,
enforce security policy, or own cloud persistence.

## Included in the first UI slice

The current UI separates local protection and setup from optional VEIL Cloud
features. It includes:

- **Protection** — shows Engine and connector readiness. The current build
  reports that protection is off and does not inspect prompts or block leaks.
- **Setup** — explains the Engine, optional local processing, and supported-app
  setup boundaries. Installation and connector configuration are not implemented.
- **Settings** — saves an Ollama loopback URL and preferred model name locally.
  These are preferences for future Engine integration; this build does not
  connect to Ollama, install models, or use them for protection.
- **Account** — opens an in-app VEIL Cloud access dialog for sign-in or
  registration and a backend-backed password-reset flow. Password reset
  requires configured SMTP delivery and Redis storage in VEIL Cloud.
- **Program Catalog and Feedback** — separate, optional Cloud pages. The
  catalog is metadata, not a list of connected or protected apps.
- **Uninstall** — Settings can move an installed VEIL Guard macOS app bundle
  from `/Applications` or the user's `Applications` folder to the Trash. It
  does not erase Cloud data or local preferences.

The window opens at 620 × 440 and remains resizable. The Protection view is
compact at its default size; longer pages scroll within the content area.

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
  pages/          Protection, setup readiness, local settings, and separate
                  account, program-catalog, and feedback pages
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

Copy `.env.example` to `.env.development` and configure the development API
base URL before running the app. For production builds, set
`VITE_API_BASE_URL` in the build environment or configure a local
`.env.production` file. These local environment files are ignored by Git. The
app rejects missing, malformed, or non-HTTPS remote endpoints. The normal
desktop workflow is `npx tauri dev` or `npx tauri build`. Both commands run
Vite automatically: development serves the UI to Tauri's WebView locally, and
the production build embeds the generated assets into the desktop bundle. No
separate website is deployed.
`npm run build` alone only checks/builds the frontend assets and does not create
the desktop app.

On macOS Apple Silicon, `npx tauri build` creates
`src-tauri/target/release/bundle/macos/VEIL Guard.app` and a `.dmg` installer
under `src-tauri/target/release/bundle/dmg/`. Windows executables need a Windows
build host or CI runner.
