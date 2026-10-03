# VEIL Guard Engine

The **VEIL Guard Engine** is the background security and confidential-processing runtime powering **VEIL Guard**.

It is responsible for enforcing VEIL's security policies, managing protected processing sessions, controlling isolated execution environments, coordinating local AI processing, protecting sensitive data, and monitoring the runtime lifecycle.

The Engine is designed to operate independently of the VEIL Guard Interface so that security enforcement does not depend on the desktop application's window remaining open.

---

## Architecture

The Engine is structured as a modular Python package with clearly separated architectural domains.

```text
engine/
│
├── builds/
│   └── veil_guard_engine/
│       └── ...
│
├── scripts/
│   ├── build.py
│   ├── clean.py
│   └── package.py
│
├── tests/
│
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

`veil_guard_engine/` is the actual Python package.

The `builds/` layer provides the deliberate packaging boundary for the Engine, while `scripts/` contains tooling used to build, clean, and package it.

The internal package architecture will be organized into broader security-runtime domains rather than maintaining a flat collection of independent modules.

---

## Role in VEIL Guard

```text
                    VEIL GUARD
                         │
              ┌──────────┴──────────┐
              │                     │
          Interface               Engine
       React + Tauri              Python
              │                     │
              └──────────┬──────────┘
                         │
                  Local communication
                         │
                    VEIL Engine
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
    Security           Policy          Protection
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                 Protected Runtime
                         │
              ┌──────────┴──────────┐
              │                     │
           Sandbox                 AI
           Docker               Ollama
```

The Interface provides the user-facing control surface.

The Engine performs the actual security operations and runtime enforcement.

---

## Core Responsibilities

The Engine will provide the runtime foundation for:

* Security enforcement
* Policy evaluation
* Sensitive-data protection and DLP
* Protected processing sessions
* Ephemeral Docker-based sandboxing
* Local AI/LLM processing through Ollama
* Cryptographic operations and session-key management
* Secure startup and shutdown
* Cleanup and session destruction
* System and Engine monitoring
* Security and lifecycle event generation

The Engine is intended to minimize persistent copies of confidential data through controlled, session-scoped processing.

---

## Local-First Processing

VEIL Guard follows a **local-first architecture** for confidential AI workloads.

```text
User
  │
  ▼
VEIL Guard
  │
  ▼
VEIL Engine
  │
  ├── DLP
  ├── Policy
  ├── Session
  ├── Sandbox
  └── Security
          │
          ▼
      Local AI Runtime
          │
        Ollama
          │
          ▼
      Local LLM
```

Confidential workloads are intended to remain on the user's machine rather than being sent to a third-party AI provider by default.

VEIL does not claim to control retention or deletion policies of external services when data is intentionally sent outside the protected local environment.

---

## Protected Session Lifecycle

A protected session follows a controlled lifecycle:

```text
Start Session
      │
      ▼
Create Session
      │
      ▼
Generate Session Key
      │
      ▼
Load Policy
      │
      ▼
Create Sandbox
      │
      ▼
Input DLP
      │
      ▼
Policy Evaluation
      │
   ┌──┴──┐
 BLOCK  ALLOW
          │
          ▼
      Local AI
          │
          ▼
      Output DLP
          │
      ┌───┴───┐
    BLOCK   RELEASE
              │
              ▼
         Close Session
              │
              ▼
        Destroy Sandbox
              │
              ▼
      Destroy Session Key
              │
              ▼
         Audit Event
```

The lifecycle is designed around ephemeral processing and controlled cleanup rather than relying on a single deletion mechanism.

---

## Security Model

VEIL Guard's security model is based on multiple complementary controls:

* Process and system monitoring
* Explicit security policies
* Data-loss prevention
* Restricted execution environments
* Ephemeral sandboxing
* Encryption and session-scoped keys
* Controlled resource and network access
* Lifecycle-based cleanup
* Tamper-evident audit records

Docker provides an isolation boundary for protected workloads but is not treated as an absolute security guarantee. The Engine must explicitly control mounts, networking, permissions, resources, and lifecycle behavior.

---

## Technology Stack

| Component               | Technology                              |
| ----------------------- | --------------------------------------- |
| Engine                  | Python                                  |
| AI Runtime              | Ollama                                  |
| AI Models               | Local LLMs                              |
| Sandbox                 | Docker                                  |
| DLP                     | Microsoft Presidio + custom recognizers |
| Cryptography            | Python cryptographic tooling            |
| Desktop Interface       | React + Vite                            |
| Desktop Runtime         | Tauri                                   |
| Cloud Control Plane     | FastAPI                                 |
| Database                | PostgreSQL                              |
| ORM / Migrations        | SQLAlchemy + Alembic                    |
| Cache / Runtime Support | Redis                                   |
| Verification Layer      | Polygon / blockchain                    |

The Engine remains independent from the cloud control plane and desktop interface.

---

## Engine and VEIL Cloud

VEIL Cloud provides control-plane capabilities such as:

* Authentication
* Account management
* Configuration and policy synchronization
* Security notifications
* Application metadata
* Audit and verification records
* Blockchain/ledger integration

Confidential plaintext, raw prompts, raw model responses, session keys, passwords, and other sensitive processing material should not be persisted in the cloud database.

---

## Development

### Requirements

* Python
* Docker
* Ollama
* Git

Additional development dependencies are defined in:

```text
requirements.txt
```

Project and packaging configuration is defined in:

```text
pyproject.toml
```

### Running the Engine

The Engine entry point is currently:

```bash
python main.py
```

The exact runtime interface and local communication mechanism between the Engine and VEIL Guard Interface will be defined as the Engine implementation progresses.

---

## Project Structure

```text
engine/
│
├── builds/
│   └── veil_guard_engine/
│
├── scripts/
│   ├── build.py
│   ├── clean.py
│   └── package.py
│
├── tests/
│
├── .gitignore
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

The internal package structure is intentionally being developed in stages. Architectural domains will be established before individual modules and files are finalized.

---

## Packaging

The Engine uses a deliberate three-level package boundary:

```text
engine/
    │
    └── builds/
          │
          └── veil_guard_engine/
```

This structure separates:

1. The Engine project root
2. The Engine build/package boundary
3. The actual Python package

The Engine package can subsequently be built, tested, and incorporated into the complete **VEIL Guard package** and Windows distribution.

---

## Design Principles

VEIL Guard Engine is being developed around the following principles:

* **Local-first** — confidential processing should remain local whenever possible.
* **Least privilege** — components receive only the access they require.
* **Ephemeral processing** — sensitive workloads should have controlled lifecycles.
* **Policy-driven security** — actions are governed by explicit policies.
* **Defense in depth** — isolation, DLP, cryptography, monitoring, and policy enforcement complement one another.
* **Separation of concerns** — Interface, Engine, and Cloud remain distinct systems.
* **Auditable lifecycle** — important security events can be recorded and verified.
* **No plaintext on-chain** — blockchain is used for verification metadata, never confidential content.
* **Explicit guarantees** — VEIL avoids claiming deletion or forensic guarantees it cannot technically prove.

---

## Status

**Development — Architecture Phase**

The outer Engine architecture and packaging model are established. Internal security-runtime domains and their implementations are being developed incrementally.

---

## Part of VEIL

```text
VEIL
│
├── VEIL Guard
│   ├── Interface
│   └── Engine
│
└── VEIL Cloud
```

**VEIL Guard Engine** is the security runtime at the core of VEIL Guard.
