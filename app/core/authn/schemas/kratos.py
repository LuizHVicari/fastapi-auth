import datetime
from typing import Any, TypedDict
from uuid import UUID

from pydantic import BaseModel


class RecoveryAddress(BaseModel):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    value: str
    via: str


class VerifiableAddress(BaseModel):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: str
    value: str
    verified: bool
    via: str


class Identity(BaseModel):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    metadata_public: dict[str, Any] | None = None
    organization_id: UUID | None = None
    recovery_addresses: list[RecoveryAddress]
    schema_id: str
    schema_url: str
    state: str
    state_changed_at: datetime.datetime
    traits: dict[str, str]
    verifiable_addresses: list[VerifiableAddress]


class RegistrationWebhookRequest(BaseModel):
    identity: Identity


class KratosWebhookResponse(TypedDict):
    status: str
