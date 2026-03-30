from typing import Annotated

from fastapi import APIRouter, Cookie, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.oauth2.dependencies import OAuth2ServiceDep
from app.core.oauth2.services.oauth2_service import (
    ConsentPageData,
    ConsentRedirect,
    LoginPageData,
    LoginRedirect,
)

router = APIRouter(prefix="/oauth2", tags=["oauth2"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", include_in_schema=False)
async def login(
    request: Request,
    login_challenge: Annotated[str, Query()],
    oauth2_service: OAuth2ServiceDep,
    ory_kratos_session: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse | HTMLResponse:
    result = await oauth2_service.initiate_login(
        challenge=login_challenge,
        login_url=str(request.url),
        kratos_cookie=ory_kratos_session,
    )

    if isinstance(result, LoginRedirect):
        return RedirectResponse(result.url)

    return templates.TemplateResponse(
        request=request,
        name="oauth2/login.html",
        context={"kratos_login_url": result.kratos_login_url},
    )


@router.get("/consent", include_in_schema=False)
async def consent_page(
    request: Request,
    consent_challenge: Annotated[str, Query()],
    oauth2_service: OAuth2ServiceDep,
) -> RedirectResponse | HTMLResponse:
    result = await oauth2_service.initiate_consent(challenge=consent_challenge)

    if isinstance(result, ConsentRedirect):
        return RedirectResponse(result.url)

    return templates.TemplateResponse(
        request=request,
        name="oauth2/consent.html",
        context={
            "consent_challenge": result.consent_challenge,
            "client_id": result.client_id,
            "scopes": result.scopes,
        },
    )


@router.post("/consent", include_in_schema=False)
async def consent_submit(
    consent_challenge: Annotated[str, Form()],
    action: Annotated[str, Form()],
    oauth2_service: OAuth2ServiceDep,
) -> RedirectResponse:
    redirect_to = await oauth2_service.handle_consent(
        challenge=consent_challenge,
        allow=action == "allow",
    )
    return RedirectResponse(redirect_to, status_code=303)


@router.get("/logout", include_in_schema=False)
async def logout(
    logout_challenge: Annotated[str, Query()],
    oauth2_service: OAuth2ServiceDep,
) -> RedirectResponse:
    redirect_to = await oauth2_service.handle_logout(challenge=logout_challenge)
    return RedirectResponse(redirect_to)
