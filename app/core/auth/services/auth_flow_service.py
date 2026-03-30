from app.core.auth.entities import FlowUI
from app.core.auth.ports import AuthFlowProvider


class AuthFlowService:
    def __init__(self, flow_provider: AuthFlowProvider) -> None:
        self.__flow_provider = flow_provider

    async def get_login_flow(self, flow_id: str, cookies: dict[str, str]) -> FlowUI | None:
        return await self.__flow_provider.get_login_flow(flow_id, cookies)

    async def get_registration_flow(self, flow_id: str, cookies: dict[str, str]) -> FlowUI | None:
        return await self.__flow_provider.get_registration_flow(flow_id, cookies)
