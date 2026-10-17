from typing import Protocol

from veil_guard_engine.core.contracts import RequestContext


class Connector(Protocol):
    connector_id: str

    async def forward_to_provider(
        self,
        prompt: str,
        context: RequestContext,
    ) -> str:
        """Forward an assessed, non-confidential prompt to its provider."""
