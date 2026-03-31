from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import APIKeyCookie, APIKeyHeader

from app.core.authn.adapters.session_provider_kratos import KratosSessionProvider
from app.core.authn.adapters.user_repository_sql import UserRepositorySql
from app.core.authn.entities.user import User
from app.core.authn.errors import UserNotRegisteredError
from app.core.authn.services.auth_service import AuthService
from app.core.authn.services.user_service import UserService
from app.core.database.engine import DbSession

_kratos_session_token = APIKeyHeader(
    name="X-Session-Token",
    description="Ory Kratos session token.",
    auto_error=False,
)

_kratos_session_cookie = APIKeyCookie(
    name="ory_kratos_session",
    description="Ory Kratos session cookie.",
    auto_error=False,
)

KratosSessionToken = Annotated[str | None, Security(_kratos_session_token)]
KratosSessionCookie = Annotated[str | None, Security(_kratos_session_cookie)]


def get_session_provider() -> KratosSessionProvider:
    return KratosSessionProvider()


SessionProviderDep = Annotated[KratosSessionProvider, Depends(get_session_provider)]


def get_user_repository(db: DbSession) -> UserRepositorySql:
    return UserRepositorySql(db)


UserRepositoryDep = Annotated[UserRepositorySql, Depends(get_user_repository)]


def get_auth_service(session_provider: SessionProviderDep) -> AuthService:
    return AuthService(session_provider)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_user_service(user_repository: UserRepositoryDep) -> UserService:
    return UserService(user_repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_auth_provider_user_id(
    auth_service: AuthServiceDep,
    x_session_token: KratosSessionToken = None,
    ory_kratos_session: KratosSessionCookie = None,
) -> UUID:
    return await auth_service.get_auth_provider_user_id(x_session_token, ory_kratos_session)


CurrentAuthProviderUserId = Annotated[UUID, Depends(get_auth_provider_user_id)]


async def get_current_user(
    auth_provider_user_id: CurrentAuthProviderUserId,
    user_service: UserServiceDep,
) -> User:
    user = await user_service.get_user_by_auth_provider_id(str(auth_provider_user_id))
    if user is None:
        raise UserNotRegisteredError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
