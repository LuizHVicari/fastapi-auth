from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass
class TokenActive:
    subject: UUID


@dataclass
class TokenInactive:
    pass


@dataclass
class TokenProviderFailure:
    is_server_error: bool


TokenProviderResponse = TokenActive | TokenInactive | TokenProviderFailure


class TokenProvider(Protocol):
    async def introspect(self, token: str) -> TokenProviderResponse: ...
