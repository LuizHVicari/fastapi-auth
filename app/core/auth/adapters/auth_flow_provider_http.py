from typing import Any, override

import httpx

from app.core.auth.entities import FlowUI
from app.core.auth.ports import AuthFlowProvider
from app.core.env import settings


def _parse_flow_ui(data: dict[str, Any]) -> FlowUI:
    ui = data.get("ui", {})
    action: str = ui.get("action", "")
    nodes: list[Any] = ui.get("nodes", [])

    hidden_fields = [
        {"name": n["attributes"]["name"], "value": n["attributes"].get("value", "")}
        for n in nodes
        if n.get("type") == "input" and n["attributes"].get("type") == "hidden"
    ]

    messages: list[Any] = ui.get("messages") or []
    error: str | None = next((m["text"] for m in messages if m.get("type") == "error"), None)
    if error is None:
        for node in nodes:
            for msg in node.get("messages") or []:
                if msg.get("type") == "error":
                    error = msg["text"]
                    break

    return FlowUI(action=action, hidden_fields=hidden_fields, error=error)


class AuthFlowProviderHttp(AuthFlowProvider):
    async def _fetch(self, endpoint: str, flow_id: str, cookies: dict[str, str]) -> FlowUI | None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.kratos_public_url}/self-service/{endpoint}/flows",
                params={"id": flow_id},
                headers={"Accept": "application/json"},
                cookies=cookies,
            )
        if not resp.is_success:
            return None
        return _parse_flow_ui(resp.json())

    @override
    async def get_login_flow(self, flow_id: str, cookies: dict[str, str]) -> FlowUI | None:
        return await self._fetch("login", flow_id, cookies)

    @override
    async def get_registration_flow(self, flow_id: str, cookies: dict[str, str]) -> FlowUI | None:
        return await self._fetch("registration", flow_id, cookies)
