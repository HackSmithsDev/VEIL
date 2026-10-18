# VEIL Guard Installer

This component builds the macOS VEIL Guard setup application with Qt Installer
Framework (Qt IF). It packages the Tauri desktop `.app` bundle; it does not
include or install the VEIL Engine, an Engine service, Ollama, or app
connectors. Installing VEIL Guard does not enable prompt protection or require
a VEIL Cloud account.

The wizard installs into the current user's Applications directory and offers
to launch VEIL Guard when installation finishes. The app's Settings page can
launch the Qt IF maintenance tool to uninstall the installed application.

## Requirements

- macOS build host
- Node.js/npm and the Rust/Tauri build prerequisites if the desktop app is to
  be built by the installer script
- Qt Installer Framework with `binarycreator` on `PATH`, or its `bin`
  directory provided through `QTIFW_BIN_DIR`

On Apple Silicon, the official Qt Installer Framework 4.7 binary package is
Intel-only and may require Rosetta. If installed under `~/Qt`, set:

```bash
export QTIFW_BIN_DIR="$HOME/Qt/Tools/QtInstallerFramework/4.7/bin"
```

## Build

From this directory:

```bash
python3 native/scripts/build.py
```

The script builds the Tauri app bundle, stages it with the installer
configuration/package metadata, and runs Qt IF `binarycreator`. The installer
version is read from `veil-guard/interface/src-tauri/tauri.conf.json`.
Staging output is under ignored `native/build/`; the setup app is written to
ignored `native/dist/`.

For a local unsigned test package:

```bash
python3 native/scripts/build.py --allow-unsigned
```

Unsigned output is for local testing only, not distribution. Release
distribution requires platform-appropriate signing and notarization.

To stage an already-built app bundle without invoking Qt IF:

```bash
python3 native/scripts/build.py --skip-app-build --stage-only
```

This still requires an existing Tauri app bundle at
`veil-guard/interface/src-tauri/target/release/bundle/macos/VEIL Guard.app`.
The `--stage-only` mode checks/stages the payload but does not create a setup
application.

## Tests

The script tests use Python's standard library and do not require Qt IF:

```bash
python3 -m unittest discover -s native/tests -v
```

They cover tool discovery, Tauri command construction, payload staging,
version synchronization, and installer bundle metadata.

## Scope and limitations

Only the macOS Qt IF package target is configured. Windows and Linux
installers, Engine service installation, Engine/IPC integration,
upgrade/repair behavior, and active protection are not implemented. See the
[Interface](../interface/README.md) and [Engine](../engine/README.md)
documentation for the related project status.
