# VEIL Guard Engine

The Engine is the planned local runtime for VEIL Guard's confidential
processing. It is separate from the desktop Interface and VEIL Cloud. The
current package contains processing contracts, policy-driven request routing,
and an experimental credential-pattern policy. It does not monitor applications,
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
The connector registry accepts only explicitly registered connector IDs; the
current package does not include a provider connector or application capture
implementation.

`VeilEngine` receives a confidentiality policy, a local processor, and a
`ConnectorRegistry`. `process_prompt` resolves the requested connector before
assessing the prompt. An unregistered connector is rejected; a confidential
prompt is sent only to the local processor; a non-confidential prompt is sent
to the registered connector. Policy or local-processing errors propagate and
never cause a remote fallback. `end_session` delegates cleanup to the local
processor.

## Package boundaries

```text
libs/veil_guard_engine/
  connectors/   Explicitly configured provider connector contract and registry
  core/         Request/result contracts and policy-driven routing
  policy/       Local confidentiality assessment interface and policy
  processing/   Local processor contract
tests/          Routing, policy, and package-script tests
```

Cloud API calls and local Engine calls are separate channels. Prompt contents,
confidential values, and local model responses must not be sent to VEIL Cloud.
The Engine should not log prompt/response bodies; diagnostics should use
minimal, non-sensitive event metadata. Provider integrations, application
capture, process supervision, and authenticated Interface-to-Engine IPC are
not implemented yet; add their packages when those components have concrete
contracts and implementations.

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

Install the optional pytest dependency and run the suite from the Engine
directory:

```bash
cd veil-guard/engine
python3 -m pip install -e ".[test]"
pytest -v
pytest -q
```

The tests can also be run without pytest:

```bash
cd veil-guard/engine
PYTHONPATH=libs:scripts python3 -m unittest discover -s tests
```

The package and contracts are not yet a deployable background service. Do not
expose Engine controls in the desktop UI until a provider connector and app
capture implementation, production-grade policy and local processor, secure
IPC, and platform installer have been implemented and reviewed.

## Package scripts

From this directory:

```bash
python3 scripts/build.py                 # build wheel and source archive
python3 scripts/build.py --format wheel  # wheel only
python3 scripts/build.py --format sdist  # source archive only
python3 scripts/clean.py                # remove known build outputs
```

Artifacts are written to `dist/`. The clean script only removes the Engine's
known `build/`, `dist/`, and package metadata outputs.