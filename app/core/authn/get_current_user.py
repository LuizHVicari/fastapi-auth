import datetime
from typing import Annotated, TypedDict
from uuid import UUID

import httpx
from fastapi import Cookie, Depends, Header, HTTPException, status

from app.core.env import settings


class SessionIdentity(TypedDict):
    id: UUID
    traits: dict[str, str]


class Session(TypedDict):
    id: UUID
    active: bool
    expires_at: datetime.datetime
    identity: SessionIdentity


async def get_current_user(
    x_session_token: Annotated[str | None, Header()] = None,
    ory_kratos_session: Annotated[str | None, Cookie()] = None,
) -> UUID:
    if x_session_token is None and ory_kratos_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session token"
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.kratos_public_url}/sessions/whoami",
            headers={"X-Session-Token": x_session_token} if x_session_token else {},
            cookies={"ory_kratos_session": ory_kratos_session} if ory_kratos_session else {},
        )
    if not response.is_success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token"
        )
    session: Session = response.json()
    return UUID(str(session["identity"]["id"]))


CurrentUser = Annotated[UUID, Depends(get_current_user)]
