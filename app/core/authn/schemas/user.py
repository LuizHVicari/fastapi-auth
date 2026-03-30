from typing import TypedDict
from uuid import UUID

from pydantic import BaseModel


class UserRequest(BaseModel):
    name: str
    avatar_url: str | None


class UserResponse(BaseModel):
    id: UUID
    auth_provider_id: str
    name: str
    avatar_url: str | None
    created_at: str
    updated_at: str


class CurrentUserResponse(TypedDict):
    user_id: UUID
