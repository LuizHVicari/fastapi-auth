import httpx

from app.core.oauth2.errors.hydra_unavailable_error import HydraUnavailableError
from app.core.oauth2.errors.invalid_challenge_error import InvalidChallengeError
from app.core.oauth2.ports import HydraProvider


class OAuth2Service:
    def __init__(self, hydra_provider: HydraProvider) -> None:
        self.__hydra = hydra_provider

    async def handle_login(self, challenge: str, kratos_subject: str | None) -> str:
        """Process a Hydra login challenge.

        If the session is already known to Hydra (skip=True), accepts immediately.
        Otherwise requires a Kratos subject to accept the challenge.
        Returns the redirect URL to send the user to.
        """
        try:
            login = await self.__hydra.get_login_challenge(challenge)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (404, 410):
                raise InvalidChallengeError(challenge) from e
            raise HydraUnavailableError() from e
        except httpx.RequestError as e:
            raise HydraUnavailableError() from e

        if login.skip or kratos_subject is not None:
            subject = login.subject if login.skip else kratos_subject
            if subject is None:
                raise InvalidChallengeError(challenge)
            return await self.__hydra.accept_login(challenge, subject, remember=True)

        return await self.__hydra.reject_login(
            challenge, "login_required", "User is not authenticated"
        )

    async def handle_consent(self, challenge: str) -> str:
        """Process a Hydra consent challenge.

        Auto-accepts all requested scopes. Returns the redirect URL.
        """
        try:
            consent = await self.__hydra.get_consent_challenge(challenge)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (404, 410):
                raise InvalidChallengeError(challenge) from e
            raise HydraUnavailableError() from e
        except httpx.RequestError as e:
            raise HydraUnavailableError() from e

        return await self.__hydra.accept_consent(
            challenge, consent.requested_scope, consent.subject
        )

    async def handle_logout(self, challenge: str) -> str:
        """Process a Hydra logout challenge. Returns the redirect URL."""
        try:
            await self.__hydra.get_logout_challenge(challenge)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (404, 410):
                raise InvalidChallengeError(challenge) from e
            raise HydraUnavailableError() from e
        except httpx.RequestError as e:
            raise HydraUnavailableError() from e

        return await self.__hydra.accept_logout(challenge)
