from typing import Protocol
from uuid import UUID

from app.core.authn.entities import User


class UserRepository(Protocol):
    async def find_user_by_id(self, user_id: UUID) -> User | None: ...

    async def find_user_by_auth_provider_id(self, auth_provider_id: str) -> User | None: ...

    async def create_user(self, user: User) -> User: ...

    async def update_user(self, user: User) -> User: ...
