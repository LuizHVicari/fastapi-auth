from dataclasses import dataclass
from urllib.parse import urlencode

from app.core.authn.ports.session_provider import ProviderSuccess, SessionProvider
from app.core.env import settings
from app.core.oauth2.errors import InvalidChallengeError
from app.core.oauth2.ports import OAuth2ChallengeProvider


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginRedirect:
    url: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginPageData:
    kratos_login_url: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ConsentRedirect:
    url: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ConsentPageData:
    consent_challenge: str
    client_id: str
    scopes: list[str]


class OAuth2Service:
    def __init__(self, provider: OAuth2ChallengeProvider, session_provider: SessionProvider) -> None:
        self.__provider = provider
        self.__session_provider = session_provider

    async def __resolve_subject(self, cookie: str | None) -> str | None:
        if cookie is None:
            return None
        result = await self.__session_provider.fetch_session(token=None, cookie=cookie)
        if isinstance(result, ProviderSuccess):
            return str(result.session.identity.id)
        return None

    async def initiate_login(
        self, challenge: str, login_url: str, kratos_cookie: str | None
    ) -> LoginRedirect | LoginPageData:
        subject = await self.__resolve_subject(kratos_cookie)
        if subject is not None:
            url = await self.__provider.accept_login(challenge, subject, remember=True)
            return LoginRedirect(url=url)

        login = await self.__provider.get_login_challenge(challenge)
        if login.skip:
            if login.subject is None:
                raise InvalidChallengeError(challenge)
            url = await self.__provider.accept_login(challenge, login.subject, remember=True)
            return LoginRedirect(url=url)

        kratos_login_url = (
            f"{settings.kratos_public_url}/self-service/login/browser"
            f"?{urlencode({'return_to': login_url})}"
        )
        return LoginPageData(kratos_login_url=kratos_login_url)

    async def initiate_consent(self, challenge: str) -> ConsentRedirect | ConsentPageData:
        consent = await self.__provider.get_consent_challenge(challenge)
        if consent.skip:
            url = await self.__provider.accept_consent(
                challenge, consent.requested_scope, consent.subject
            )
            return ConsentRedirect(url=url)

        return ConsentPageData(
            consent_challenge=challenge,
            client_id=consent.client_id,
            scopes=consent.requested_scope,
        )

    async def handle_consent(self, challenge: str, allow: bool) -> str:
        consent = await self.__provider.get_consent_challenge(challenge)

        if not allow:
            return await self.__provider.reject_consent(
                challenge, "access_denied", "User denied access"
            )

        return await self.__provider.accept_consent(
            challenge, consent.requested_scope, consent.subject
        )

    async def handle_logout(self, challenge: str) -> str:
        await self.__provider.get_logout_challenge(challenge)
        return await self.__provider.accept_logout(challenge)
