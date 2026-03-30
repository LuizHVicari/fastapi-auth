from typing import Protocol

from app.core.auth.entities import FlowUI


class AuthFlowProvider(Protocol):
    async def get_login_flow(self, flow_id: str, cookies: dict[str, str]) -> FlowUI | None:
        """Fetch and parse a Kratos login flow. Returns None if expired/invalid."""
        ...

    async def get_registration_flow(self, flow_id: str, cookies: dict[str, str]) -> FlowUI | None:
        """Fetch and parse a Kratos registration flow. Returns None if expired/invalid."""
        ...
