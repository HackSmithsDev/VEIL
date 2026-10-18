from collections.abc import Iterable

from veil_guard_engine.connectors.base import Connector


class ConnectorRegistry:
    """Allow the Engine to route requests only through configured connectors."""

    def __init__(self, connectors: Iterable[Connector] = ()) -> None:
        self._connectors: dict[str, Connector] = {}
        for connector in connectors:
            self.register(connector)

    def register(self, connector: Connector) -> None:
        connector_id = connector.connector_id
        if not connector_id or connector_id.strip() != connector_id:
            raise ValueError("Connector ID must be a non-empty, trimmed string")
        if connector_id in self._connectors:
            raise ValueError(f"Connector ID is already registered: {connector_id}")
        self._connectors[connector_id] = connector

    def get(self, connector_id: str) -> Connector:
        try:
            return self._connectors[connector_id]
        except KeyError as error:
            raise LookupError(
                f"No connector is registered with ID: {connector_id}"
            ) from error
