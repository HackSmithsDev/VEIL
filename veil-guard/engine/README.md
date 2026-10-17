# VEIL Guard Engine

The Engine is the planned local runtime for VEIL Guard's confidential
processing. It is separate from the desktop Interface and VEIL Cloud. The
current package contains the processing contracts, routing skeleton, and an
experimental credential-pattern policy. It does not monitor applications,
provide comprehensive confidential-content detection, run Ollama, or install a
background service.

## Intended request flow

1. A supported, explicitly configured connector captures one AI request.
2. The local policy component assesses the prompt before it can be forwarded.
3. Non-confidential prompts may be forwarded by that connector to its provider.
4. Confidential prompts are never sent through the connector. They are handed
   to the local processor, and its result is returned to the connector.
5. The connector renders the selected result in the originating application.
6. When a session ends, the Engine tells the local processor to close its
   session and release session state.

The package includes an experimental local pattern policy for a limited set of
recognizable credential formats. It is not comprehensive DLP and can miss
secrets or produce false positives; it is not sufficient to claim production
credential-leak prevention. There is no Ollama integration. Policy errors must
not silently fall back to forwarding a prompt. A future connector must document
its supported app, capture mechanism, response rendering, and failure behavior.

## Package boundaries

```text
libs/veil_guard_engine/
  connectors/   Explicitly supported app/provider adapters and registry
  core/         Request/result contracts and local-vs-remote orchestration
  policy/       Confidentiality assessment interface and policy models
  processing/   Local processor interface (future Ollama implementation)
  runtime/      Session lifecycle and process supervision boundaries
  ipc/          Future authenticated local Interface-to-Engine contract
tests/          Engine routing and lifecycle tests
```

Cloud API calls and local Engine calls are separate channels. Prompt contents,
confidential values, and local model responses must not be sent to VEIL Cloud.
The Engine should not log prompt/response bodies; diagnostics should use
minimal, non-sensitive event metadata.

## Process and installation model

Do not run the whole Engine as an administrator just because it operates in the
background. The eventual installer should put signed, non-writable binaries in
the platform's application location and store mutable state separately. Use the
least-privileged service/agent identity that supports a specific connector.
Windows services and macOS launch agents/daemons require separate packaging,
permissions, signing, upgrade, and uninstall work.

Use a narrow local IPC endpoint for the desktop Interface. It must authenticate
the local client, validate message sizes and schemas, and not listen on a
network-facing interface. App connectors should be opt-in and scoped to named
applications; broad system-wide prompt interception is not part of this design.

## Ollama and session cleanup

Ollama is a local processing dependency, not a disposable Docker container.
Ending a session should stop/unload the session's model work and clear
VEIL-managed temporary session data. Do not uninstall Ollama or delete shared
model weights after each session. Whether model memory can be reliably cleared
is platform/runtime-dependent and must be stated honestly in the UX.

## Development status

The current scaffold can be exercised with the standard library test runner:

```bash
python3 -m unittest discover -s tests
```

The package and contracts are not yet a deployable background service. Do not
expose Engine controls in the desktop UI until a connector, policy
implementation, local processor, IPC security model, and platform installer
have been implemented and reviewed.