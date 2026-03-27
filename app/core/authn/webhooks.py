import datetime
import hmac
from typing import Annotated, Any, TypedDict
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from app.core.env import settings

router = APIRouter(prefix="/webhooks")


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


@router.post("/kratos/registration")
async def kratos_registration_webhook(
    body: RegistrationWebhookRequest, x_kratos_secret: Annotated[str | None, Header()] = None
) -> KratosWebhookResponse:
    if x_kratos_secret is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing webhook secret"
        )
    are_secrets_equal = hmac.compare_digest(
        x_kratos_secret, settings.kratos_webhook_secret.get_secret_value()
    )
    if not are_secrets_equal:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret"
        )
    print("Received Kratos registration webhook:", body)
    return {"status": "received"}
