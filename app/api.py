from typing import TypedDict

from fastapi import FastAPI

from .core.authn import authn_router, authn_webhooks_router

app = FastAPI()

app.include_router(authn_webhooks_router)
app.include_router(authn_router)


class HealthResponse(TypedDict):
    status: str


@app.get("/health")
async def health() -> HealthResponse:
    return {"status": "ok"}
