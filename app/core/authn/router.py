from typing import TypedDict
from uuid import UUID

from fastapi import APIRouter

from app.core.authn.get_current_user import CurrentUser

router = APIRouter(prefix="/authn")


class CurrentUserResponse(TypedDict):
    user_id: UUID


@router.get("/current-user")
async def current_user(user: CurrentUser) -> CurrentUserResponse:
    return {"user_id": user}
