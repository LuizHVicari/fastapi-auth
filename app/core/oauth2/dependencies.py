from typing import Annotated

from fastapi import Depends

from app.core.oauth2.adapters.hydra_provider_hydra import HydraProviderHydra
from app.core.oauth2.services.oauth2_service import OAuth2Service


def get_hydra_provider() -> HydraProviderHydra:
    return HydraProviderHydra()


HydraProviderDep = Annotated[HydraProviderHydra, Depends(get_hydra_provider)]


def get_oauth2_service(hydra_provider: HydraProviderDep) -> OAuth2Service:
    return OAuth2Service(hydra_provider)


OAuth2ServiceDep = Annotated[OAuth2Service, Depends(get_oauth2_service)]
