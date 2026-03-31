import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateApiKeyRequest(BaseModel):
    description: str | None = Field(
        default=None, max_length=1000, description="Description of the API key."
    )
    duration_days: int = Field(
        default=30,
        gt=0,
        lt=366,
        description="Duration of the API key in days. Must be between 1 and 365.",
    )


class ApiKeyResponse(BaseModel):
    key_string: str = Field(
        ..., description="The API key string in the format 'public_key:private_key'."
    )


class ListApiKeysResponseItem(BaseModel):
    id: UUID
    public_key: str
    description: str | None
    expires_at: datetime.datetime | None
    is_revoked: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ListApiKeysResponse(BaseModel):
    items: tuple[ListApiKeysResponseItem, ...]
    total: int
