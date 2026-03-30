import hmac
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status

from app.core.authn.schemas import KratosWebhookResponse, RegistrationWebhookRequest
from app.core.env import settings

router = APIRouter(prefix="/webhooks")


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
