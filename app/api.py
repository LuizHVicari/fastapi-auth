import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypedDict

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from loguru import logger
from opentelemetry import trace as otel_trace
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.env import settings
from app.core.shared.errors import AppError
from app.core.telemetry import setup_logging, setup_tracing

setup_logging()

from .core.auth.http import auth_router
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

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(authn_webhooks_router)
app.include_router(authn_router)
app.include_router(oauth2_router)


@app.middleware("http")
async def request_logging(request: Request, call_next: Any) -> Any:  # noqa: ANN401
    start = time.perf_counter()

    response = await call_next(request)

    span = otel_trace.get_current_span()
    ctx = span.get_span_context()
    trace_id = format(ctx.trace_id, "032x") if ctx.is_valid else "no-trace"

    logger.info(
        "{method} {path} {status_code} {duration}s",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=round(time.perf_counter() - start, 4),
        trace_id=trace_id,
        client=request.client.host if request.client else None,
    )

    response.headers["X-Trace-ID"] = trace_id
    return response


class HealthResponse(TypedDict):
    status: str


@app.get("/health")
async def health() -> HealthResponse:
    return {"status": "ok"}


@app.exception_handler(AppError)
async def handle_app_error(_request: Any, exc: AppError) -> None:  # noqa: ANN401
    raise HTTPException(status_code=exc.status_code, detail=exc.message)
