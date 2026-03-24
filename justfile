# runs the server in development mode
start-dev host="0.0.0.0" port="8000":
    uv run fastapi dev app/api.py --host {{host}} --port {{port}}

# starts auxiliary services for development in Docker
start-infra:
    docker compose --profile infra --profile dev up -d --remove-orphans

# stops auxiliary services for development
stop-infra:
    docker compose --profile infra --profile dev down --remove-orphans

# removes all auxiliary services for development, including volumes and images
delete-infra:
    docker compose --profile infra --profile dev down -v --rmi all --remove-orphans

# starts the server and auxiliary services for development in Docker
start-docker:
    docker compose --profile infra --profile dev --profile app up -d --remove-orphans