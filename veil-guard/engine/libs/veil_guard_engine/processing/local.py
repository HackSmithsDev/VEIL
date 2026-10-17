from typing import Protocol

from veil_guard_engine.core.contracts import RequestContext


class LocalProcessor(Protocol):
    async def process_locally(
        self,
        prompt: str,
        context: RequestContext,
    ) -> str:
        """Process a confidential prompt without sending it to a remote provider."""

    async def end_session(self, context: RequestContext) -> None:
        """Release local processing state associated with a session."""
