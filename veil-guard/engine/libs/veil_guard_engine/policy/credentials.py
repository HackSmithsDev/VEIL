import re

from veil_guard_engine.core.contracts import PolicyDecision, RequestContext

_CREDENTIAL_PATTERNS = (
    (
        "private_key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "bearer_token",
        re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{16,}={0,2}", re.IGNORECASE),
    ),
    (
        "credential_assignment",
        re.compile(
            r"""(?i)\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|"""
            r"""client[_-]?secret|password|secret)\b\s*[:=]\s*"""
            r"""["']?[^\s"'`,;]{8,}"""
        ),
    ),
)


class CredentialPatternPolicy:
    """Detect a limited set of recognizable credential formats locally."""

    async def assess(
        self,
        prompt: str,
        context: RequestContext,
    ) -> PolicyDecision:
        del context
        reason_codes = tuple(
            code
            for code, pattern in _CREDENTIAL_PATTERNS
            if pattern.search(prompt)
        )
        return PolicyDecision(
            confidential=bool(reason_codes),
            reason_codes=reason_codes,
        )
