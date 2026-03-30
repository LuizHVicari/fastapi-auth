from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypedDict

from fastapi import FastAPI, HTTPException

from app.core.env import settings
from app.core.shared.errors import AppError

from .core.authn.http import authn_router, authn_webhooks_router
from .core.database import engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)  # validates connectivity on startup
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    description="Authenticated via Ory Kratos — use either `X-Session-Token` header or `ory_kratos_session` cookie.",
)

app.include_router(authn_webhooks_router)
app.include_router(authn_router)


class HealthResponse(TypedDict):
    status: str


@app.get("/health")
async def health() -> HealthResponse:
    return {"status": "ok"}


@app.exception_handler(AppError)
async def handle_app_error(_request: Any, exc: AppError) -> None:  # noqa: ANN401
    raise HTTPException(status_code=exc.status_code, detail=exc.message)
