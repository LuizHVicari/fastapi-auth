from typing import override
from uuid import UUID

import httpx

from app.core.authn.ports import TokenProvider
from app.core.authn.ports.token_provider import (
    TokenActive,
    TokenInactive,
    TokenProviderFailure,
    TokenProviderResponse,
)
from app.core.env import settings


class HydraTokenProvider(TokenProvider):
    @override
    async def introspect(self, token: str) -> TokenProviderResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.hydra_admin_url}/admin/oauth2/introspect",
                data={"token": token},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code >= 500:
            return TokenProviderFailure(is_server_error=True)

        if not response.is_success:
            return TokenProviderFailure(is_server_error=False)

        data = response.json()

        if not data.get("active"):
            return TokenInactive()

        return TokenActive(subject=UUID(str(data["sub"])))
