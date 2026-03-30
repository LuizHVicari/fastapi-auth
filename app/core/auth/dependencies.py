from typing import Annotated

from fastapi import Depends

from app.core.auth.adapters import AuthFlowProviderHttp
from app.core.auth.services import AuthFlowService


def get_flow_provider() -> AuthFlowProviderHttp:
    return AuthFlowProviderHttp()


FlowProviderDep = Annotated[AuthFlowProviderHttp, Depends(get_flow_provider)]


def get_auth_flow_service(flow_provider: FlowProviderDep) -> AuthFlowService:
    return AuthFlowService(flow_provider)


AuthFlowServiceDep = Annotated[AuthFlowService, Depends(get_auth_flow_service)]
