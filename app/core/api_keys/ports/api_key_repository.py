from typing import Literal, Protocol
from uuid import UUID

from app.core.api_keys.entities import ApiKey
from app.utils.pagination_utils import Paginated


class ApiKeyRepository(Protocol):
    async def create_api_key(self, api_key: ApiKey) -> ApiKey: ...

    async def find_api_key_by_public_key(self, public_key: str) -> ApiKey | None: ...

    async def update_api_key(self, api_key: ApiKey) -> ApiKey: ...

    async def list_api_keys(
        self,
        *,
        user_id: UUID | None = None,
        expired: bool | None = None,
        description: str | None = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Literal["created_at"]
        | Literal["updated_at"]
        | Literal["description"]
        | Literal["user_id"] = "created_at",
        order_direction: Literal["asc"] | Literal["desc"] = "asc",
    ) -> Paginated[ApiKey]: ...
