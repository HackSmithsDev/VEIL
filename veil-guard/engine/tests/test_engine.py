import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "libs"))

from veil_guard_engine.connectors.registry import ConnectorRegistry  # noqa: E402
from veil_guard_engine.core.contracts import (  # noqa: E402
    PolicyDecision,
    ProcessingRoute,
    RequestContext,
)
from veil_guard_engine.core.engine import VeilEngine  # noqa: E402
from veil_guard_engine.policy.credentials import CredentialPatternPolicy  # noqa: E402


class FakePolicy:
    def __init__(self, decision: PolicyDecision) -> None:
        self.decision = decision
        self.assessed: list[str] = []

    async def assess(self, prompt: str, context: RequestContext) -> PolicyDecision:
        self.assessed.append(prompt)
        return self.decision


class RaisingPolicy:
    async def assess(self, prompt: str, context: RequestContext) -> PolicyDecision:
        raise RuntimeError("policy unavailable")


class FakeConnector:
    connector_id = "test"

    def __init__(self) -> None:
        self.forwarded: list[str] = []

    async def forward_to_provider(
        self,
        prompt: str,
        context: RequestContext,
    ) -> str:
        self.forwarded.append(prompt)
        return "remote response"


class FakeLocalProcessor:
    def __init__(self) -> None:
        self.processed: list[str] = []
        self.ended_sessions: list[str] = []

    async def process_locally(
        self,
        prompt: str,
        context: RequestContext,
    ) -> str:
        self.processed.append(prompt)
        return "local response"

    async def end_session(self, context: RequestContext) -> None:
        self.ended_sessions.append(context.session_id)


def create_engine(
    policy: FakePolicy | RaisingPolicy | CredentialPatternPolicy,
    local: FakeLocalProcessor,
    *connectors: FakeConnector,
) -> VeilEngine:
    return VeilEngine(policy, local, ConnectorRegistry(connectors))


class RaisingLocalProcessor(FakeLocalProcessor):
    async def process_locally(
        self,
        prompt: str,
        context: RequestContext,
    ) -> str:
        raise RuntimeError("local processor unavailable")


class EngineRoutingTests(unittest.IsolatedAsyncioTestCase):
    async def test_confidential_prompt_never_reaches_connector(self) -> None:
        connector = FakeConnector()
        local = FakeLocalProcessor()
        engine = create_engine(
            FakePolicy(PolicyDecision(confidential=True, reason_codes=("secret",))),
            local,
            connector,
        )
        context = RequestContext(connector_id="test", session_id="session-1")

        result = await engine.process_prompt("sensitive prompt", context)

        self.assertEqual(result.route, ProcessingRoute.LOCAL)
        self.assertEqual(result.response, "local response")
        self.assertEqual(result.reason_codes, ("secret",))
        self.assertEqual(local.processed, ["sensitive prompt"])
        self.assertEqual(connector.forwarded, [])

    async def test_non_confidential_prompt_uses_connector(self) -> None:
        connector = FakeConnector()
        local = FakeLocalProcessor()
        engine = create_engine(
            FakePolicy(PolicyDecision(confidential=False)),
            local,
            connector,
        )
        context = RequestContext(connector_id="test", session_id="session-1")

        result = await engine.process_prompt("ordinary prompt", context)

        self.assertEqual(result.route, ProcessingRoute.REMOTE)
        self.assertEqual(result.response, "remote response")
        self.assertEqual(connector.forwarded, ["ordinary prompt"])
        self.assertEqual(local.processed, [])

    async def test_session_end_is_forwarded_to_local_processor(self) -> None:
        connector = FakeConnector()
        local = FakeLocalProcessor()
        engine = create_engine(
            FakePolicy(PolicyDecision(confidential=True)),
            local,
            connector,
        )
        context = RequestContext(connector_id="test", session_id="session-2")

        await engine.end_session(context)

        self.assertEqual(local.ended_sessions, ["session-2"])

    async def test_credential_pattern_policy_detects_common_secret_formats(self) -> None:
        policy = CredentialPatternPolicy()
        context = RequestContext(connector_id="test", session_id="session-3")
        prompt = (
            "Use api_key=example-secret-value and this "
            "-----BEGIN PRIVATE KEY----- block."
        )

        decision = await policy.assess(prompt, context)

        self.assertTrue(decision.confidential)
        self.assertEqual(
            decision.reason_codes,
            ("private_key", "credential_assignment"),
        )
        self.assertNotIn("example-secret-value", " ".join(decision.reason_codes))

    async def test_credential_pattern_policy_leaves_plain_prompt_unclassified(self) -> None:
        policy = CredentialPatternPolicy()
        context = RequestContext(connector_id="test", session_id="session-4")

        decision = await policy.assess("Explain how API keys work.", context)

        self.assertFalse(decision.confidential)
        self.assertEqual(decision.reason_codes, ())

    async def test_credential_policy_supports_provider_token_patterns(self) -> None:
        policy = CredentialPatternPolicy()
        context = RequestContext(connector_id="test", session_id="session-7")
        examples = (
            ("AKIA1234567890ABCDEF", "aws_access_key"),
            ("ghp_" + "A" * 32, "github_token"),
            ("xoxb-12345678-12345678", "slack_token"),
            ("Bearer " + "A" * 24, "bearer_token"),
        )

        for prompt, expected_code in examples:
            with self.subTest(expected_code=expected_code):
                decision = await policy.assess(prompt, context)
                self.assertTrue(decision.confidential)
                self.assertIn(expected_code, decision.reason_codes)
                self.assertNotIn(prompt, " ".join(decision.reason_codes))

    async def test_detected_credential_prompt_routes_only_to_local_processor(self) -> None:
        connector = FakeConnector()
        local = FakeLocalProcessor()
        engine = create_engine(CredentialPatternPolicy(), local, connector)
        context = RequestContext(connector_id="test", session_id="session-5")
        prompt = "My password: example-password-value"

        result = await engine.process_prompt(prompt, context)

        self.assertEqual(result.route, ProcessingRoute.LOCAL)
        self.assertEqual(local.processed, [prompt])
        self.assertEqual(connector.forwarded, [])

    async def test_unregistered_connector_is_rejected_before_policy_assessment(self) -> None:
        connector = FakeConnector()
        local = FakeLocalProcessor()
        policy = FakePolicy(PolicyDecision(confidential=False))
        engine = create_engine(policy, local)
        context = RequestContext(connector_id="unknown", session_id="session-6")

        with self.assertRaisesRegex(LookupError, "No connector is registered"):
            await engine.process_prompt("ordinary prompt", context)

        self.assertEqual(policy.assessed, [])
        self.assertEqual(connector.forwarded, [])

    async def test_policy_error_does_not_forward_prompt(self) -> None:
        connector = FakeConnector()
        engine = create_engine(RaisingPolicy(), FakeLocalProcessor(), connector)
        context = RequestContext(connector_id="test", session_id="session-8")

        with self.assertRaisesRegex(RuntimeError, "policy unavailable"):
            await engine.process_prompt("unassessed prompt", context)

        self.assertEqual(connector.forwarded, [])

    async def test_local_processor_error_does_not_fall_back_to_connector(self) -> None:
        connector = FakeConnector()
        engine = create_engine(
            FakePolicy(PolicyDecision(confidential=True)),
            RaisingLocalProcessor(),
            connector,
        )
        context = RequestContext(connector_id="test", session_id="session-9")

        with self.assertRaisesRegex(RuntimeError, "local processor unavailable"):
            await engine.process_prompt("sensitive prompt", context)

        self.assertEqual(connector.forwarded, [])

    async def test_registry_rejects_duplicate_and_invalid_connector_ids(self) -> None:
        registry = ConnectorRegistry()
        registry.register(FakeConnector())

        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register(FakeConnector())

        class InvalidConnector(FakeConnector):
            connector_id = " test "

        with self.assertRaisesRegex(ValueError, "non-empty, trimmed"):
            registry.register(InvalidConnector())


if __name__ == "__main__":
    unittest.main()
