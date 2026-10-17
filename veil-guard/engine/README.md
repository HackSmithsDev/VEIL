# VEIL Guard Engine

The Engine is the planned local runtime for VEIL Guard's confidential
processing. It is separate from both the desktop Interface and VEIL Cloud.

## Boundary

- The **Interface** presents controls and calls cloud resources for accounts,
  profile details, program metadata, and feedback.
- The **Cloud** authenticates users and persists those account-scoped records.
- The **Engine**, in a later phase, will own local protected processing. It is
  not required for the initial account/program/feedback release.

Do not interpret the Engine's planned capabilities as implemented. Sandboxing,
DLP, policy evaluation, local model execution, cryptography, and audit behavior
need individual designs and security validation before being exposed in the UI.

## Current layout

```text
engine/
  libs/veil_guard_engine/   Python package source
  scripts/                  Build and packaging helpers
  tests/                    Engine tests
  main.py                   Planned runtime entry point
  pyproject.toml            Python project configuration
  requirements.txt          Runtime dependencies
```

Keep package source and packaging configuration in one canonical layout; avoid
maintaining duplicate `builds/` and `libs/` package trees. The package and
entry-point configuration still need to be completed before the Engine can be
run as a product component.

## Later integration

When the Engine is implemented, the desktop app should communicate with it
through a narrowly defined local IPC contract. Cloud API calls and local Engine
calls are separate channels: confidential processing inputs must not be sent to
VEIL Cloud unless a separately reviewed product requirement explicitly
requires it.