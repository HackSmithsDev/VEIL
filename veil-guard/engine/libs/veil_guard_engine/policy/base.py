from typing import Protocol

from veil_guard_engine.core.contracts import PolicyDecision, RequestContext


class ConfidentialityPolicy(Protocol):
    async def assess(
        self,
        prompt: str,
        context: RequestContext,
    ) -> PolicyDecision:
        """Assess a prompt locally before any connector can forward it."""
