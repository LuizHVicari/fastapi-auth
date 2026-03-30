from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security

from app.core.authn.adapters.session_provider_kratos import KratosSessionProvider
from app.core.authn.adapters.token_provider_hydra import HydraTokenProvider
from app.core.authn.adapters.user_repository_sql import UserRepositorySql
from app.core.authn.entities.user import User
from app.core.authn.security import hydra_oauth2, kratos_session_cookie, kratos_session_token
from app.core.authn.services.auth_service import AuthService
from app.core.authn.services.user_service import UserService
from app.core.database.engine import DbSession


def get_session_provider() -> KratosSessionProvider:
    return KratosSessionProvider()


SessionProviderDep = Annotated[KratosSessionProvider, Depends(get_session_provider)]


def get_token_provider() -> HydraTokenProvider:
    return HydraTokenProvider()


TokenProviderDep = Annotated[HydraTokenProvider, Depends(get_token_provider)]


def get_user_repository(db: DbSession) -> UserRepositorySql:
    return UserRepositorySql(db)


UserRepositoryDep = Annotated[UserRepositorySql, Depends(get_user_repository)]


def get_auth_service(
    session_provider: SessionProviderDep,
    token_provider: TokenProviderDep,
) -> AuthService:
    return AuthService(session_provider, token_provider)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_user_service(user_repository: UserRepositoryDep) -> UserService:
    return UserService(user_repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_auth_provider_user_id(
    auth_service: AuthServiceDep,
    x_session_token: Annotated[str | None, Security(kratos_session_token)] = None,
    ory_kratos_session: Annotated[str | None, Security(kratos_session_cookie)] = None,
    bearer: Annotated[str | None, Security(hydra_oauth2)] = None,
) -> UUID:
    return await auth_service.get_auth_provider_user_id(x_session_token, ory_kratos_session, bearer)


AuthProviderUserIdDep = Annotated[UUID, Depends(get_auth_provider_user_id)]


async def get_current_user(
    auth_provider_user_id: AuthProviderUserIdDep,
    user_service: UserServiceDep,
) -> User:
    return await user_service.get_user_by_auth_provider_id(str(auth_provider_user_id))


CurrentUser = Annotated[User, Depends(get_current_user)]
