from uuid import uuid7

from fastapi import APIRouter

from app.core.authn.dependencies import CurrentAuthProviderUserId, CurrentUser, UserServiceDep
from app.core.authn.entities.user import User
from app.core.authn.schemas import CurrentUserResponse, UserRequest, UserResponse
from app.utils.time_utils import now_utc

router = APIRouter(prefix="/authn")


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        auth_provider_id=user.auth_provider_id,
        name=user.name,
        avatar_url=user.avatar_url,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )


@router.get("/current-user")
async def current_user(user: CurrentUser) -> CurrentUserResponse:
    return {"user_id": user.id}


@router.post("/profile")
async def create_profile(
    request: UserRequest,
    auth_provider_user_id: CurrentAuthProviderUserId,
    user_service: UserServiceDep,
) -> UserResponse:
    now = now_utc()
    user = await user_service.create_user(
        User(
            id=uuid7(),
            auth_provider_id=str(auth_provider_user_id),
            name=request.name,
            avatar_url=request.avatar_url,
            created_at=now,
            updated_at=now,
        )
    )
    return _to_user_response(user)


@router.put("/profile")
async def update_profile(
    request: UserRequest, current_user: CurrentUser, user_service: UserServiceDep
) -> UserResponse:
    now = now_utc()
    user = await user_service.update_user(
        User(
            id=current_user.id,
            auth_provider_id=current_user.auth_provider_id,
            name=request.name,
            avatar_url=request.avatar_url,
            created_at=current_user.created_at,
            updated_at=now,
        )
    )
    return _to_user_response(user)
