from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import APIKeyCookie, APIKeyHeader

from app.core.api_keys.dependencies import ApiKeyServiceDep
from app.core.api_keys.services import ApiKeyService
from app.core.authn.adapters import KratosSessionProvider, UserRepositorySql
from app.core.authn.entities import User
from app.core.authn.errors import UserNotRegisteredError
from app.core.authn.errors.invalid_session_error import InvalidSessionError
from app.core.authn.ports import SessionProvider, UserRepository
from app.core.authn.services import AuthService, UserService
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

_api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="API key for authentication.",
    auto_error=False,
)

KratosSessionToken = Annotated[str | None, Security(_kratos_session_token)]
KratosSessionCookie = Annotated[str | None, Security(_kratos_session_cookie)]
ApiKeyHeader = Annotated[str | None, Security(_api_key_header)]


def get_session_provider() -> SessionProvider:
    return KratosSessionProvider()


SessionProviderDep = Annotated[SessionProvider, Depends(get_session_provider)]


def get_user_repository(db: DbSession) -> UserRepository:
    return UserRepositorySql(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


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


async def _resolve_user_from_session(
    auth_service: AuthService,
    user_service: UserService,
    x_session_token: str | None,
    ory_kratos_session: str | None,
) -> User | None:
    if not x_session_token and not ory_kratos_session:
        return None
    auth_provider_user_id = await auth_service.get_auth_provider_user_id(
        x_session_token, ory_kratos_session
    )
    return await user_service.get_user_by_auth_provider_id(str(auth_provider_user_id))


async def _resolve_user_from_api_key(
    api_key_service: ApiKeyService,
    user_service: UserService,
    x_api_key: str | None,
) -> User | None:
    if not x_api_key:
        return None
    api_key = await api_key_service.validate_api_key(x_api_key)
    if not api_key.can_be_used:
        raise InvalidSessionError()
    return await user_service.find_user_by_id(api_key.user_id)


async def get_current_user(
    auth_service: AuthServiceDep,
    api_key_service: ApiKeyServiceDep,
    user_service: UserServiceDep,
    x_session_token: KratosSessionToken = None,
    x_api_key: ApiKeyHeader = None,
    ory_kratos_session: KratosSessionCookie = None,
) -> User:
    user = await _resolve_user_from_session(
        auth_service, user_service, x_session_token, ory_kratos_session
    )
    user = user or await _resolve_user_from_api_key(api_key_service, user_service, x_api_key)

    if user is None:
        raise UserNotRegisteredError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
