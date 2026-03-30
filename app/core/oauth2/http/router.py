from typing import Annotated

from fastapi import APIRouter, Cookie, Query
from fastapi.responses import RedirectResponse

from app.core.authn.adapters.session_provider_kratos import KratosSessionProvider
from app.core.authn.ports.session_provider import ProviderSuccess
from app.core.oauth2.dependencies import OAuth2ServiceDep

router = APIRouter(prefix="/oauth2", tags=["oauth2"])

_kratos = KratosSessionProvider()


async def _get_kratos_subject(cookie: str | None) -> str | None:
    """Attempt to resolve a Kratos identity ID from the session cookie."""
    if cookie is None:
        return None
    result = await _kratos.fetch_session(token=None, cookie=cookie)
    if isinstance(result, ProviderSuccess):
        return str(result.session.identity.id)
    return None


@router.get("/login", include_in_schema=False)
async def login(
    login_challenge: Annotated[str, Query()],
    oauth2_service: OAuth2ServiceDep,
    ory_kratos_session: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    """Hydra login callback — resolves the Kratos session and accepts/rejects the challenge."""
    subject = await _get_kratos_subject(ory_kratos_session)
    redirect_to = await oauth2_service.handle_login(login_challenge, subject)
    return RedirectResponse(redirect_to)


@router.get("/consent", include_in_schema=False)
async def consent(
    consent_challenge: Annotated[str, Query()],
    oauth2_service: OAuth2ServiceDep,
) -> RedirectResponse:
    """Hydra consent callback — auto-accepts all requested scopes."""
    redirect_to = await oauth2_service.handle_consent(consent_challenge)
    return RedirectResponse(redirect_to)


@router.get("/logout", include_in_schema=False)
async def logout(
    logout_challenge: Annotated[str, Query()],
    oauth2_service: OAuth2ServiceDep,
) -> RedirectResponse:
    """Hydra logout callback — accepts the logout challenge."""
    redirect_to = await oauth2_service.handle_logout(logout_challenge)
    return RedirectResponse(redirect_to)
