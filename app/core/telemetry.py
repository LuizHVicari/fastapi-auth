import logging
import sys
from typing import override

from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.sqlalchemy import (  # pyright: ignore[reportMissingTypeStubs]
    SQLAlchemyInstrumentor,  # type: ignore[import-untyped]
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.env import settings

_resource = Resource({SERVICE_NAME: settings.app_name})


class _LoguruHandler(logging.Handler):
    @override
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _otlp_http_base() -> str:
    # gRPC endpoint is e.g. http://localhost:4317 — OTLP HTTP lives on 4318
    return settings.otel_exporter_endpoint.replace("4317", "4318")


def _grpc_endpoint() -> str:
    # OTLPSpanExporter (gRPC) expects "host:port" without scheme
    return settings.otel_exporter_endpoint.removeprefix("http://").removeprefix("https://")


def setup_logging() -> None:
    log_provider = LoggerProvider(resource=_resource)
    log_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{_otlp_http_base()}/v1/logs"))
    )
    otel_handler = LoggingHandler(logger_provider=log_provider)

    is_tty = sys.stdout.isatty()
    logger.remove()
    logger.add(
        sys.stdout,
        serialize=not is_tty,
        colorize=is_tty,
        level=settings.log_level.upper(),
        backtrace=True,
        diagnose=False,
    )
    logger.add(
        otel_handler,
        level=settings.log_level.upper(),
        format="{message}",
    )

    # redirect stdlib logging (uvicorn, sqlalchemy, etc.) into loguru
    logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.WARNING, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy"):
        log = logging.getLogger(name)
        log.handlers = [_LoguruHandler()]
        log.propagate = False


def setup_tracing(engine: AsyncEngine) -> None:
    provider = TracerProvider(resource=_resource)
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=_grpc_endpoint(), insecure=True))
    )
    trace.set_tracer_provider(provider)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
