from veil_guard_engine.connectors.base import Connector
from veil_guard_engine.connectors.registry import ConnectorRegistry
from veil_guard_engine.core.contracts import (
    PolicyDecision,
    ProcessingResult,
    ProcessingRoute,
    RequestContext,
)
from veil_guard_engine.policy.base import ConfidentialityPolicy
from veil_guard_engine.processing.local import LocalProcessor


class VeilEngine:
    def __init__(
        self,
        policy: ConfidentialityPolicy,
        local_processor: LocalProcessor,
        connectors: ConnectorRegistry,
    ) -> None:
        self._policy = policy
        self._local_processor = local_processor
        self._connectors = connectors

    async def process_prompt(
        self,
        prompt: str,
        context: RequestContext,
    ) -> ProcessingResult:
        connector: Connector = self._connectors.get(context.connector_id)

        decision: PolicyDecision = await self._policy.assess(prompt, context)
        if decision.confidential:
            response = await self._local_processor.process_locally(prompt, context)
            return ProcessingResult(
                response=response,
                route=ProcessingRoute.LOCAL,
                reason_codes=decision.reason_codes,
            )

        response = await connector.forward_to_provider(prompt, context)
        return ProcessingResult(response=response, route=ProcessingRoute.REMOTE)

    async def end_session(self, context: RequestContext) -> None:
        await self._local_processor.end_session(context)
