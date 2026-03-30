from typing import override

import httpx

from app.core.env import settings
from app.core.oauth2.entities.challenge import ConsentChallenge, LoginChallenge, LogoutChallenge
from app.core.oauth2.ports import HydraProvider


class HydraProviderHydra(HydraProvider):
    """Ory Hydra Admin API adapter for OAuth2 challenge flows."""

    @override
    async def get_login_challenge(self, challenge: str) -> LoginChallenge:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{settings.hydra_admin_url}/admin/oauth2/auth/requests/login",
                params={"login_challenge": challenge},
            )
            r.raise_for_status()
            data = r.json()
        return LoginChallenge(
            challenge=challenge,
            subject=data.get("subject"),
            skip=data["skip"],
            requested_scope=data.get("requested_scope") or [],
            client_id=data["client"]["client_id"],
        )

    @override
    async def accept_login(self, challenge: str, subject: str, remember: bool) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.put(
                f"{settings.hydra_admin_url}/admin/oauth2/auth/requests/login/accept",
                params={"login_challenge": challenge},
                json={"subject": subject, "remember": remember, "remember_for": 3600},
            )
            r.raise_for_status()
        return str(r.json()["redirect_to"])

    @override
    async def reject_login(self, challenge: str, error: str, description: str) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.put(
                f"{settings.hydra_admin_url}/admin/oauth2/auth/requests/login/reject",
                params={"login_challenge": challenge},
                json={"error": error, "error_description": description},
            )
            r.raise_for_status()
        return str(r.json()["redirect_to"])

    @override
    async def get_consent_challenge(self, challenge: str) -> ConsentChallenge:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{settings.hydra_admin_url}/admin/oauth2/auth/requests/consent",
                params={"consent_challenge": challenge},
            )
            r.raise_for_status()
            data = r.json()
        return ConsentChallenge(
            challenge=challenge,
            subject=data["subject"],
            skip=data["skip"],
            requested_scope=data.get("requested_scope") or [],
            client_id=data["client"]["client_id"],
        )

    @override
    async def accept_consent(
        self, challenge: str, granted_scope: list[str], subject: str
    ) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.put(
                f"{settings.hydra_admin_url}/admin/oauth2/auth/requests/consent/accept",
                params={"consent_challenge": challenge},
                json={
                    "grant_scope": granted_scope,
                    "remember": True,
                    "remember_for": 3600,
                    "session": {"id_token": {"sub": subject}},
                },
            )
            r.raise_for_status()
        return str(r.json()["redirect_to"])

    @override
    async def reject_consent(self, challenge: str, error: str, description: str) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.put(
                f"{settings.hydra_admin_url}/admin/oauth2/auth/requests/consent/reject",
                params={"consent_challenge": challenge},
                json={"error": error, "error_description": description},
            )
            r.raise_for_status()
        return str(r.json()["redirect_to"])

    @override
    async def get_logout_challenge(self, challenge: str) -> LogoutChallenge:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{settings.hydra_admin_url}/admin/oauth2/auth/requests/logout",
                params={"logout_challenge": challenge},
            )
            r.raise_for_status()
            data = r.json()
        return LogoutChallenge(
            challenge=challenge,
            subject=data.get("subject"),
            sid=data.get("sid"),
        )

    @override
    async def accept_logout(self, challenge: str) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.put(
                f"{settings.hydra_admin_url}/admin/oauth2/auth/requests/logout/accept",
                params={"logout_challenge": challenge},
            )
            r.raise_for_status()
        return str(r.json()["redirect_to"])
