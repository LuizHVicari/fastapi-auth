from dataclasses import dataclass
from typing import Protocol

from app.core.authn.entities.session import Session


@dataclass
class ProviderSuccess:
    session: Session


@dataclass
class ProviderFailure:
    is_server_error: bool


ProviderResponse = ProviderSuccess | ProviderFailure


class SessionProvider(Protocol):
    async def fetch_session(self, token: str | None, cookie: str | None) -> ProviderResponse: ...
