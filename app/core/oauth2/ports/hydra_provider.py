from typing import Protocol

from app.core.oauth2.entities.challenge import ConsentChallenge, LoginChallenge, LogoutChallenge


class HydraProvider(Protocol):
    """Abstraction over the Ory Hydra Admin API for OAuth2 challenge flows."""

    async def get_login_challenge(self, challenge: str) -> LoginChallenge:
        """Fetch a login challenge from Hydra by its challenge string."""
        ...

    async def accept_login(self, challenge: str, subject: str, remember: bool) -> str:
        """Accept a login challenge and return the redirect URL."""
        ...

    async def reject_login(self, challenge: str, error: str, description: str) -> str:
        """Reject a login challenge and return the redirect URL."""
        ...

    async def get_consent_challenge(self, challenge: str) -> ConsentChallenge:
        """Fetch a consent challenge from Hydra by its challenge string."""
        ...

    async def accept_consent(
        self, challenge: str, granted_scope: list[str], subject: str
    ) -> str:
        """Accept a consent challenge and return the redirect URL."""
        ...

    async def reject_consent(self, challenge: str, error: str, description: str) -> str:
        """Reject a consent challenge and return the redirect URL."""
        ...

    async def get_logout_challenge(self, challenge: str) -> LogoutChallenge:
        """Fetch a logout challenge from Hydra by its challenge string."""
        ...

    async def accept_logout(self, challenge: str) -> str:
        """Accept a logout challenge and return the redirect URL."""
        ...
