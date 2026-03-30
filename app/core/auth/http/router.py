import contextlib
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Cookie, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.auth.dependencies import AuthFlowServiceDep
from app.core.authn.adapters.session_provider_kratos import KratosSessionProvider
from app.core.authn.adapters.user_repository_sql import UserRepositorySql
from app.core.authn.entities.user import User
from app.core.authn.errors import UserAlreadyExistsError
from app.core.authn.ports.session_provider import ProviderSuccess
from app.core.authn.services.user_service import UserService
from app.core.database.engine import DbSession
from app.core.env import settings
from app.utils.time_utils import now_utc

router = APIRouter(prefix="/auth", include_in_schema=False)
templates = Jinja2Templates(directory="templates")
_kratos = KratosSessionProvider()


@router.get("/login")
async def login_page(
    request: Request,
    auth_flow_service: AuthFlowServiceDep,
    flow: Annotated[str | None, Query()] = None,
) -> RedirectResponse | HTMLResponse:
    if flow is None:
        return RedirectResponse(f"{settings.kratos_public_url}/self-service/login/browser")

    ui = await auth_flow_service.get_login_flow(flow, dict(request.cookies))
    if ui is None:
        return RedirectResponse(f"{settings.kratos_public_url}/self-service/login/browser")

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "action": ui.action,
            "hidden_fields": ui.hidden_fields,
            "error": ui.error,
            "registration_url": "/auth/registration",
        },
    )


@router.get("/registration")
async def registration_page(
    request: Request,
    auth_flow_service: AuthFlowServiceDep,
    flow: Annotated[str | None, Query()] = None,
) -> RedirectResponse | HTMLResponse:
    if flow is None:
        return RedirectResponse(f"{settings.kratos_public_url}/self-service/registration/browser")

    ui = await auth_flow_service.get_registration_flow(flow, dict(request.cookies))
    if ui is None:
        return RedirectResponse(f"{settings.kratos_public_url}/self-service/registration/browser")

    return templates.TemplateResponse(
        request=request,
        name="auth/registration.html",
        context={
            "action": ui.action,
            "hidden_fields": ui.hidden_fields,
            "error": ui.error,
            "login_url": "/auth/login",
        },
    )


@router.get("/setup-profile")
async def setup_profile_page(
    request: Request,
    return_to: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="auth/setup_profile.html",
        context={"return_to": return_to, "error": error},
    )


@router.post("/setup-profile")
async def setup_profile_submit(
    db: DbSession,
    ory_kratos_session: Annotated[str | None, Cookie()] = None,
    name: Annotated[str, Form()] = "",
    avatar_url: Annotated[str | None, Form()] = None,
    return_to: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    result = await _kratos.fetch_session(token=None, cookie=ory_kratos_session)
    if not isinstance(result, ProviderSuccess):
        return RedirectResponse("/auth/login", status_code=303)

    auth_provider_id = str(result.session.identity.id)
    now = now_utc()
    user_service = UserService(UserRepositorySql(db))

    with contextlib.suppress(UserAlreadyExistsError):
        await user_service.create_user(
            User(
                id=uuid4(),
                auth_provider_id=auth_provider_id,
                name=name.strip(),
                avatar_url=avatar_url or None,
                created_at=now,
                updated_at=now,
            )
        )

    if return_to:
        return RedirectResponse(return_to, status_code=303)
    return RedirectResponse("/", status_code=303)
