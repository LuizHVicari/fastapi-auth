import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypedDict

from fastapi import FastAPI, HTTPException, Request
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.env import settings
from app.core.shared.errors import AppError
from app.core.telemetry import setup_logging, setup_tracing

setup_logging()

from .core.authn.http import authn_router, authn_webhooks_router
from .core.database import engine
from .core.oauth2.http import router as oauth2_router

setup_tracing(engine)

# FastAPIInstrumentor must be called before the FastAPI app is created
from opentelemetry.instrumentation.fastapi import (  # pyright: ignore[reportMissingTypeStubs]
    FastAPIInstrumentor,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)  # validates connectivity on startup
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    description=(
        "Authenticated via Ory Kratos (browser) or Ory Hydra OAuth2 (API/MCP clients). "
        "Browser clients use `X-Session-Token` header or `ory_kratos_session` cookie. "
        "API clients use the Authorization Code flow documented below."
    ),
)

Instrumentator().instrument(app).expose(app)
FastAPIInstrumentor.instrument_app(app)

app.include_router(authn_webhooks_router)
app.include_router(authn_router)
app.include_router(oauth2_router)


@app.middleware("http")
async def request_logging(request: Request, call_next: Any) -> Any:  # noqa: ANN401
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    response = await call_next(request)

    logger.info(
        "{method} {path} {status_code} {duration}s",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=round(time.perf_counter() - start, 4),
        request_id=request_id,
        client=request.client.host if request.client else None,
    )

    response.headers["X-Request-ID"] = request_id
    return response


class HealthResponse(TypedDict):
    status: str


@app.get("/health")
async def health() -> HealthResponse:
    return {"status": "ok"}


@app.exception_handler(AppError)
async def handle_app_error(_request: Any, exc: AppError) -> None:  # noqa: ANN401
    raise HTTPException(status_code=exc.status_code, detail=exc.message)
