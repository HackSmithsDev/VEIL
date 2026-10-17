from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class RequestContext:
    connector_id: str
    session_id: str


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    confidential: bool
    reason_codes: tuple[str, ...] = ()


class ProcessingRoute(StrEnum):
    REMOTE = "remote"
    LOCAL = "local"


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    response: str
    route: ProcessingRoute
    reason_codes: tuple[str, ...] = ()
