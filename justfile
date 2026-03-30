

# starts auxiliary services for development in Docker (API runs locally)
start-infra:
    KRATOS_ENV_FILE=kratos.env.yml docker compose --profile infra --profile dev up -d --remove-orphans

# stops auxiliary services for development
stop-infra:
    docker compose --profile infra --profile dev down --remove-orphans

# removes all auxiliary services for development, including volumes and images
delete-infra:
    docker compose --profile infra --profile dev down -v --rmi all --remove-orphans

# starts the server and auxiliary services for development in Docker (API runs in Docker)
start-docker:
    KRATOS_ENV_FILE=kratos.env.docker.yml docker compose --profile infra --profile dev --profile app up -d --remove-orphans

# reloads Alloy config without full restart
reload-obs:
    curl -s -X POST http://localhost:12345/-/reload && echo "Alloy reloaded"

# starts observability stack (Grafana, Loki, Alloy, Prometheus, Tempo)
start-obs:
    docker compose --profile observability up -d --remove-orphans

# stops observability stack
stop-obs:
    docker compose --profile observability down --remove-orphans

# removes observability stack including volumes
delete-obs:
    docker compose --profile observability down -v --remove-orphans

# starts infra + observability
start-all:
    KRATOS_ENV_FILE=kratos.env.yml docker compose --profile infra --profile dev --profile observability up -d --remove-orphans

# stops infra + observability
stop-all:
    docker compose --profile infra --profile dev --profile observability down --remove-orphans

# removes infra + observability including volumes
delete-all:
    docker compose --profile infra --profile dev --profile observability down -v --rmi all --remove-orphans

# run type checker and linter
check:
    uv run pyright
    uv run ruff check

start-dev port="" host="":
    uv run fastapi dev app/api.py {{ if host != "" { "--host " + host } else { "" } }} {{ if port != "" { "--port " + port } else { "" } }}


docker-logs service="" tail="100" follow="false":
    docker compose logs {{ if follow == "true" { "-f" } else { "" } }} --tail={{ tail }} {{ service }}


# generate a new migration (requires running infra)
migrate-generate name:
    uv run alembic revision --autogenerate -m "{{ name }}"

# apply all pending migrations (requires running infra)
migrate-up:
    uv run alembic upgrade head

# rollback last migration
migrate-down:
    uv run alembic downgrade -1

# show current migration state
migrate-status:
    uv run alembic current

# show migration history
migrate-history:
    uv run alembic history --verbose


# generate 32 character random secrets
generate-secrets:
    @echo "Generating secrets for Kratos..."
    @echo "Cookie Secret: $(openssl rand -base64 32)"
    @echo "Cipher Secret: $(openssl rand -hex 16)"
    @echo "Webhook Secret: $(openssl rand -base64 32)"
    @echo ""
    @echo "Generating secrets for Hydra..."
    @echo "System Secret: $(openssl rand -hex 32)"