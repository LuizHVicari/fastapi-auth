import datetime
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Cookie, Depends, Header, HTTPException, status

from app.core.env import settings


@dataclass
class SessionIdentity:
    id: UUID
    traits: dict[str, str]


@dataclass
class Session:
    id: UUID
    active: bool
    expires_at: datetime.datetime
    identity: SessionIdentity


@dataclass
class ProviderSuccess:
    session: Session


@dataclass
class ProviderFailure:
    is_server_error: bool


ProviderResponse = ProviderSuccess | ProviderFailure


async def fetch_from_provider(token: str | None, cookie: str | None) -> ProviderResponse:
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


async def get_current_user(
    x_session_token: Annotated[str | None, Header()] = None,
    ory_kratos_session: Annotated[str | None, Cookie()] = None,
) -> UUID:
    if x_session_token is None and ory_kratos_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session token"
        )

    result = await fetch_from_provider(x_session_token, ory_kratos_session)

    if isinstance(result, ProviderFailure):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            if result.is_server_error
            else status.HTTP_401_UNAUTHORIZED,
            detail="Auth service unavailable"
            if result.is_server_error
            else "Invalid session token",
        )

    return result.session.identity.id


CurrentUser = Annotated[UUID, Depends(get_current_user)]
