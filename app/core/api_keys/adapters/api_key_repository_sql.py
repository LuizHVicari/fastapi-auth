from typing import Literal, override
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api_keys.entities import ApiKey
from app.core.api_keys.errors import ApiKeyNotFoundError
from app.core.api_keys.ports import ApiKeyRepository
from app.core.database.models import ApiKeyTable
from app.utils.pagination_utils import Paginated
from app.utils.sql_utils import escape_like


class ApiKeyRepositorySql(ApiKeyRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self.__db_session = db_session

    @override
    async def create_api_key(self, api_key: ApiKey) -> ApiKey:
        new_api_key = self.__entity_to_model(api_key)
        self.__db_session.add(new_api_key)
        await self.__db_session.flush()
        await self.__db_session.refresh(new_api_key)
        return self.__model_to_entity(new_api_key)

    @override
    async def find_api_key_by_public_key(self, public_key: str) -> ApiKey | None:
        result = await self.__db_session.execute(
            select(ApiKeyTable).where(ApiKeyTable.public_key == public_key)
        )
        api_key_model = result.scalar_one_or_none()
        if api_key_model is None:
            return None

        return self.__model_to_entity(api_key_model)

    @override
    async def update_api_key(self, api_key: ApiKey) -> ApiKey:
        update_api_key_stmt = select(ApiKeyTable).where(ApiKeyTable.id == api_key.id)
        update_api_key_result = await self.__db_session.execute(update_api_key_stmt)

        api_key_model = update_api_key_result.scalar_one_or_none()
        if api_key_model is None:
            raise ApiKeyNotFoundError(key_id=api_key.id)

        api_key_model.public_key = api_key.public_key
        api_key_model.private_key_hash = api_key.secret_hash
        api_key_model.description = api_key.description
        api_key_model.user_id = api_key.user_id
        api_key_model.expires_at = api_key.expires_at
        api_key_model.is_revoked = api_key.is_revoked
        api_key_model.created_at = api_key.created_at
        api_key_model.updated_at = api_key.updated_at

        self.__db_session.add(api_key_model)
        await self.__db_session.flush()
        await self.__db_session.refresh(api_key_model)
        return self.__model_to_entity(api_key_model)

    @override
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
    ) -> Paginated[ApiKey]:
        query = select(ApiKeyTable)

        if user_id is not None:
            query = query.where(ApiKeyTable.user_id == user_id)

        if expired is not None and expired is True:
            query = query.where(ApiKeyTable.expires_at < func.now())
        if expired is not None and expired is False:
            query = query.where(ApiKeyTable.expires_at >= func.now())

        if description is not None:
            query = query.where(ApiKeyTable.description.ilike(f"%{escape_like(description)}%"))

        total_result = await self.__db_session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.scalar_one()

        order_column = getattr(ApiKeyTable, order_by)
        query = query.order_by(
            order_column.asc() if order_direction == "asc" else order_column.desc()
        )
        query = query.limit(limit).offset(offset)
        items_result = await self.__db_session.execute(query)
        items = items_result.scalars().all()

        return Paginated(items=tuple(self.__model_to_entity(item) for item in items), total=total)

    def __model_to_entity(self, api_key_model: ApiKeyTable) -> ApiKey:
        return ApiKey(
            id=api_key_model.id,
            public_key=api_key_model.public_key,
            secret_hash=api_key_model.private_key_hash,
            description=api_key_model.description,
            user_id=api_key_model.user_id,
            expires_at=api_key_model.expires_at,
            is_revoked=api_key_model.is_revoked,
            created_at=api_key_model.created_at,
            updated_at=api_key_model.updated_at,
        )

    def __entity_to_model(self, api_key: ApiKey) -> ApiKeyTable:
        return ApiKeyTable(
            id=api_key.id,
            public_key=api_key.public_key,
            private_key_hash=api_key.secret_hash,
            description=api_key.description,
            user_id=api_key.user_id,
            expires_at=api_key.expires_at,
            is_revoked=api_key.is_revoked,
            created_at=api_key.created_at,
            updated_at=api_key.updated_at,
        )
