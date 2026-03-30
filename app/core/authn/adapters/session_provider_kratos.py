from typing import override
from uuid import UUID

import httpx

from app.core.authn.entities.session import Session, SessionIdentity
from app.core.authn.ports.session_provider import ProviderFailure, ProviderResponse, ProviderSuccess
from app.core.env import settings


class KratosSessionProvider:
    @override
    async def fetch_session(self, token: str | None, cookie: str | None) -> ProviderResponse:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.kratos_public_url}/sessions/whoami",
                headers={"X-Session-Token": token} if token else {},
                cookies={"ory_kratos_session": cookie} if cookie else {},
            )

        if response.status_code >= 500:
            return ProviderFailure(is_server_error=True)

        if not response.is_success:
            return ProviderFailure(is_server_error=False)

        data = response.json()
        return ProviderSuccess(
            session=Session(
                id=UUID(str(data["id"])),
                active=data["active"],
                expires_at=data["expires_at"],
                identity=SessionIdentity(
                    id=UUID(str(data["identity"]["id"])),
                    traits=data["identity"]["traits"],
                ),
            ),
        )
