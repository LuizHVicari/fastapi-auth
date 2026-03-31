from uuid import UUID

from app.core.authn.errors import (
    AuthProviderUnavailableError,
    InvalidSessionError,
    MissingSessionTokenError,
)
from app.core.authn.ports import ProviderFailure, SessionProvider


class AuthService:
    def __init__(self, session_provider: SessionProvider) -> None:
        self.__session_provider = session_provider

    async def get_auth_provider_user_id(
        self,
        token: str | None,
        cookie: str | None,
    ) -> UUID:
        if token is None and cookie is None:
            raise MissingSessionTokenError()

        result = await self.__session_provider.fetch_session(token, cookie)

        if isinstance(result, ProviderFailure) and result.is_server_error:
            raise AuthProviderUnavailableError()
        if isinstance(result, ProviderFailure):
            raise InvalidSessionError()

        return result.session.identity.id
