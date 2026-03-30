from uuid import UUID

from app.core.authn.errors import (
    AuthProviderUnavailableError,
    InvalidSessionError,
    MissingSessionTokenError,
)
from app.core.authn.ports import ProviderFailure, SessionProvider, TokenProviderFailure
from app.core.authn.ports.token_provider import TokenInactive, TokenProvider


class AuthService:
    def __init__(
        self,
        session_provider: SessionProvider,
        token_provider: TokenProvider,
    ) -> None:
        self.__session_provider = session_provider
        self.__token_provider = token_provider

    async def get_auth_provider_user_id(
        self,
        token: str | None,
        cookie: str | None,
        bearer: str | None,
    ) -> UUID:
        if bearer is not None:
            return await self.__introspect_bearer(bearer)

        if token is None and cookie is None:
            raise MissingSessionTokenError()

        result = await self.__session_provider.fetch_session(token, cookie)

        if isinstance(result, ProviderFailure):
            if result.is_server_error:
                raise AuthProviderUnavailableError()
            raise InvalidSessionError()

        return result.session.identity.id

    async def __introspect_bearer(self, bearer: str) -> UUID:
        result = await self.__token_provider.introspect(bearer)

        if isinstance(result, TokenProviderFailure):
            if result.is_server_error:
                raise AuthProviderUnavailableError()
            raise InvalidSessionError()

        if isinstance(result, TokenInactive):
            raise InvalidSessionError()

        return result.subject
