from typing import override

import httpx

from app.core.env import settings
from app.core.oauth2.entities.challenge import ConsentChallenge, LoginChallenge, LogoutChallenge
from app.core.oauth2.errors import HydraUnavailableError, InvalidChallengeError
from app.core.oauth2.ports import OAuth2ChallengeProvider


class OAuth2ChallengeProviderHttp(OAuth2ChallengeProvider):
    async def _get(self, path: str, params: dict[str, str]) -> dict[str, object]:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{settings.hydra_admin_url}{path}", params=params)
                r.raise_for_status()
                return r.json()  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (404, 410):
                raise InvalidChallengeError(params.get("login_challenge") or params.get("consent_challenge") or params.get("logout_challenge") or "") from e
            raise HydraUnavailableError() from e
        except httpx.RequestError as e:
            raise HydraUnavailableError() from e

    async def _put(self, path: str, params: dict[str, str], json: object) -> dict[str, object]:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.put(f"{settings.hydra_admin_url}{path}", params=params, json=json)
                r.raise_for_status()
                return r.json()  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (404, 410):
                raise InvalidChallengeError("") from e
            raise HydraUnavailableError() from e
        except httpx.RequestError as e:
            raise HydraUnavailableError() from e

    @override
    async def get_login_challenge(self, challenge: str) -> LoginChallenge:
        data = await self._get(
            "/admin/oauth2/auth/requests/login",
            {"login_challenge": challenge},
        )
        return LoginChallenge(
            challenge=challenge,
            subject=data.get("subject"),  # type: ignore[arg-type]
            skip=data["skip"],  # type: ignore[arg-type]
            requested_scope=data.get("requested_scope") or [],  # type: ignore[arg-type]
            client_id=data["client"]["client_id"],  # type: ignore[index]
        )

    @override
    async def accept_login(self, challenge: str, subject: str, remember: bool) -> str:
        data = await self._put(
            "/admin/oauth2/auth/requests/login/accept",
            {"login_challenge": challenge},
            {"subject": subject, "remember": remember, "remember_for": 3600},
        )
        return str(data["redirect_to"])

    @override
    async def reject_login(self, challenge: str, error: str, description: str) -> str:
        data = await self._put(
            "/admin/oauth2/auth/requests/login/reject",
            {"login_challenge": challenge},
            {"error": error, "error_description": description},
        )
        return str(data["redirect_to"])

    @override
    async def get_consent_challenge(self, challenge: str) -> ConsentChallenge:
        data = await self._get(
            "/admin/oauth2/auth/requests/consent",
            {"consent_challenge": challenge},
        )
        return ConsentChallenge(
            challenge=challenge,
            subject=data["subject"],  # type: ignore[arg-type]
            skip=data["skip"],  # type: ignore[arg-type]
            requested_scope=data.get("requested_scope") or [],  # type: ignore[arg-type]
            client_id=data["client"]["client_id"],  # type: ignore[index]
        )

    @override
    async def accept_consent(self, challenge: str, granted_scope: list[str], subject: str) -> str:
        data = await self._put(
            "/admin/oauth2/auth/requests/consent/accept",
            {"consent_challenge": challenge},
            {
                "grant_scope": granted_scope,
                "remember": True,
                "remember_for": 3600,
                "session": {"id_token": {"sub": subject}},
            },
        )
        return str(data["redirect_to"])

    @override
    async def reject_consent(self, challenge: str, error: str, description: str) -> str:
        data = await self._put(
            "/admin/oauth2/auth/requests/consent/reject",
            {"consent_challenge": challenge},
            {"error": error, "error_description": description},
        )
        return str(data["redirect_to"])

    @override
    async def get_logout_challenge(self, challenge: str) -> LogoutChallenge:
        data = await self._get(
            "/admin/oauth2/auth/requests/logout",
            {"logout_challenge": challenge},
        )
        return LogoutChallenge(
            challenge=challenge,
            subject=data.get("subject"),  # type: ignore[arg-type]
            sid=data.get("sid"),  # type: ignore[arg-type]
        )

    @override
    async def accept_logout(self, challenge: str) -> str:
        data = await self._put(
            "/admin/oauth2/auth/requests/logout/accept",
            {"logout_challenge": challenge},
            {},
        )
        return str(data["redirect_to"])
