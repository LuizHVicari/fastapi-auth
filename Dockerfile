FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --no-dev --frozen

COPY app/ app/

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS runner

WORKDIR /app

COPY --from=builder /app /app

  CMD ["uv", "run", "fastapi", "run", "app/api.py", "--host", "0.0.0.0", "--port", "8000"]