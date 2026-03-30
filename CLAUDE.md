# Project

FastAPI server (Python 3.13+) using async SQLAlchemy, Alembic, Ory Kratos (authn) and Ory Keto (authz).

## Commands

```bash
just start-infra       # start Docker services (postgres, kratos, keto, mailpit) — API runs locally
just stop-infra        # stop Docker services
just delete-infra      # stop and remove volumes + images
just start-docker      # start everything including API in Docker
just start-dev         # run API locally with hot reload
just migrate-generate name=<name>  # generate new Alembic migration
just migrate-up        # apply pending migrations
just migrate-down      # rollback last migration
just migrate-status    # current migration state
just generate-secrets  # generate Kratos secrets
```

Run linter/formatter: `uv run ruff check` / `uv run ruff format`
Run type checker: `uv run pyright`

## Architecture

Hexagonal architecture with DDD. Each domain module under `app/core/<domain>/` follows this structure:

```
entities/       # pure domain models (no external deps)
errors/         # domain errors extending AppError (shared/errors.py)
ports/          # Protocols (interfaces) — only depend on entities
adapters/       # concrete implementations of ports
services/       # business logic — only knows entities, errors, ports
schemas/        # HTTP request/response models (Pydantic/TypedDict)
http/           # FastAPI routers — only orchestrates request → service → response
dependencies.py # composition root — instantiates adapters, wires FastAPI Depends
```

`AppError` subclasses bubble up through services and are caught by the global handler in `api.py`, which translates them to `HTTPException`. Services never import FastAPI.

Dependency chain: `http → services → ports ← adapters`. Nothing from infrastructure leaks into domain.

## Current modules

- `app/core/authn/` — authentication via Ory Kratos
  - `KratosSessionProvider` — fetches session via `/sessions/whoami`
  - `AuthService` — validates session, returns `auth_provider_user_id`
  - `UserService` — fetches/creates/updates `User` from database
  - `CurrentUser` — `Annotated[User, Depends(get_current_user)]`, use in routers
- `app/core/authz/` — authorization via Ory Keto
  - `KetAuthzProvider` — Keto REST adapter (read `:4466`, write `:4467`)
  - `AuthzService` — check/grant/revoke type and object permissions
  - `verify_type_permission(relation, object_type)` — closure dep for type-level checks
  - `verify_object_permission(relation, object_type)` — closure dep for instance-level checks (reads `object_id` from path)
  - `Relation` — StrEnum with `READER`, `WRITER`, `OWNER` as defaults

## Dependencies pattern

Each `dependencies.py` creates an `Annotated` type below every factory function:

```python
def get_foo(dep: BarDep) -> Foo:
    return Foo(dep)

FooDep = Annotated[Foo, Depends(get_foo)]
```

Use `FooDep` as the type in downstream functions — never `Depends(...)` inline.

## Database

- Single postgres container, three databases: `app` (Alembic), `kratos`, `keto`
- `app/core/database/models/base.py` — `Base` uses `settings.postgres_schema` as default schema
- Tables that need a different schema override `__table_args__ = {"schema": "other"}`
- Alembic `env.py` creates the schema if it doesn't exist and runs with `include_schemas=True`
- `POSTGRES_SCHEMA` env var controls the default schema (default: `public`)

## Keto namespaces

Defined in `keto/config/namespaces.ts` (OPL — Ory Permission Language, TypeScript).
Add new namespaces there when adding new domains. The class name becomes the `object_type` string used in `AuthzService` calls.

## Environment files

- `.env` — local dev vars (gitignored)
- `.env.example` — template
- `kratos/config/kratos.env.yml` — Kratos secrets + webhook URLs (gitignored, copy from `kratos.env.example.yml`)
- `keto/config/keto.env.yml` — Keto DSN with credentials (gitignored, copy from `keto.env.example.yml`)

## Tooling

- Package manager: `uv`
- Linter/formatter: `ruff` (line length 100, strict)
- Type checker: `pyright` (strict mode, Python 3.14 target)
- `@override` decorator required on all adapter method overrides
- Imports always from `__init__.py`, never from specific submodules directly
