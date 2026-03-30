from typing import Annotated

from fastapi import Depends

from app.core.authn.adapters import KratosSessionProvider
from app.core.oauth2.adapters import OAuth2ChallengeProviderHttp
from app.core.oauth2.services.oauth2_service import OAuth2Service


def get_oauth2_challenge_provider() -> OAuth2ChallengeProviderHttp:
    return OAuth2ChallengeProviderHttp()


OAuth2ChallengeProviderDep = Annotated[OAuth2ChallengeProviderHttp, Depends(get_oauth2_challenge_provider)]


def get_session_provider() -> KratosSessionProvider:
    return KratosSessionProvider()


SessionProviderDep = Annotated[KratosSessionProvider, Depends(get_session_provider)]


def get_oauth2_service(
    provider: OAuth2ChallengeProviderDep,
    session_provider: SessionProviderDep,
) -> OAuth2Service:
    return OAuth2Service(provider, session_provider)


OAuth2ServiceDep = Annotated[OAuth2Service, Depends(get_oauth2_service)]
