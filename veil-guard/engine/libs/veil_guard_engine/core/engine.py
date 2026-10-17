from veil_guard_engine.connectors.base import Connector
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
    ) -> None:
        self._policy = policy
        self._local_processor = local_processor

    async def process_prompt(
        self,
        prompt: str,
        context: RequestContext,
        connector: Connector,
    ) -> ProcessingResult:
        if connector.connector_id != context.connector_id:
            raise ValueError("Connector does not match request context")

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
