# VEIL Guard Installer

This folder contains the first native installer target: a branded macOS wizard
built with Qt Installer Framework. It packages the Tauri VEIL Guard desktop
app. The Engine is not included because it does not yet have a runnable service
entry point.

The Qt IF finish page offers **Launch VEIL Guard**. Installation does not
require a VEIL Cloud account. Ollama/model downloads and connector permissions
are deferred to the installed app and require user consent.

## Build

Build on macOS with Qt Installer Framework installed and `binarycreator` on
`PATH`, or set `QTIFW_BIN_DIR` to its `bin` directory:

```bash
python3 native/scripts/build.py
```

On Apple Silicon, the official Qt Installer Framework 4.7 binary package is
Intel-only and runs through Rosetta. If installed under `~/Qt`, build with:

```bash
QTIFW_BIN_DIR="$HOME/Qt/Tools/QtInstallerFramework/4.7/bin" \
  python3 native/scripts/build.py
```

For a local unsigned test build only:

```bash
python3 native/scripts/build.py --allow-unsigned
```

To stage and validate the Tauri app payload without Qt IF installed:

```bash
python3 native/scripts/build.py --skip-app-build --stage-only
```

Production distribution requires appropriate code signing and notarization.
The staged payload is created under ignored `native/build/`; installer output
goes to ignored `native/dist/`.

## Tests

```bash
python3 -m unittest discover -s native/tests -v
```

Only the macOS package target is configured. Windows and Linux packages,
Engine service installation, upgrade/repair/uninstall, and protection
activation are not implemented.
