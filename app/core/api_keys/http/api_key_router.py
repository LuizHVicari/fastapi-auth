from typing import Literal

from fastapi import APIRouter, status

from app.core.api_keys.dependencies import ApiKeyServiceDep
from app.core.api_keys.schemas import (
    ApiKeyResponse,
    CreateApiKeyRequest,
    ListApiKeysResponse,
    ListApiKeysResponseItem,
)
from app.core.authn.dependencies import CurrentUser

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_api_key(
    user: CurrentUser, api_key_service: ApiKeyServiceDep, request: CreateApiKeyRequest
) -> ApiKeyResponse:

    api_key_string = await api_key_service.generate_api_key(
        user=user, description=request.description, duration_days=request.duration_days
    )

    return ApiKeyResponse(key_string=api_key_string)


@router.get("")
async def list_user_api_keys(
    user: CurrentUser,
    api_key_service: ApiKeyServiceDep,
    expired: bool | None = None,
    description: str | None = None,
    limit: int = 100,
    offset: int = 0,
    order_by: Literal["created_at", "updated_at", "description", "user_id"] = "created_at",
    order_direction: Literal["asc", "desc"] = "asc",
) -> ListApiKeysResponse:
    api_keys_page = await api_key_service.list_user_api_keys(
        user=user,
        expired=expired,
        description=description,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_direction=order_direction,
    )

    return ListApiKeysResponse(
        items=tuple(
            ListApiKeysResponseItem(
                id=api_key.id,
                public_key=api_key.public_key,
                description=api_key.description,
                expires_at=api_key.expires_at,
                is_revoked=api_key.is_revoked,
                created_at=api_key.created_at,
                updated_at=api_key.updated_at,
            )
            for api_key in api_keys_page.items
        ),
        total=api_keys_page.total,
    )


@router.delete("/{public_key}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    user: CurrentUser, api_key_service: ApiKeyServiceDep, public_key: str
) -> None:
    await api_key_service.revoke_api_key(user=user, public_key=public_key)
