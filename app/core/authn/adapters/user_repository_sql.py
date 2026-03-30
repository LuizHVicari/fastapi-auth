from typing import override
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authn.entities import User
from app.core.authn.errors import UserNotFoundError
from app.core.authn.ports import UserRepository
from app.core.database.models import UserTable


class UserRepositorySql(UserRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self.__db_session = db_session

    @override
    async def find_user_by_id(self, user_id: UUID) -> User | None:
        result = await self.__db_session.execute(select(UserTable).where(UserTable.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return User(
            id=user.id,
            auth_provider_id=user.auth_provider_id,
            name=user.name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @override
    async def find_user_by_auth_provider_id(self, auth_provider_id: str) -> User | None:
        find_user_smtm = select(UserTable).where(UserTable.auth_provider_id == auth_provider_id)

        find_user_result = await self.__db_session.execute(find_user_smtm)
        user = find_user_result.scalar_one_or_none()

        if user is None:
            return None

        return User(
            id=user.id,
            auth_provider_id=user.auth_provider_id,
            name=user.name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @override
    async def create_user(self, user: User) -> User:
        new_user = UserTable(
            auth_provider_id=user.auth_provider_id,
            name=user.name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.__db_session.add(new_user)
        await self.__db_session.commit()
        await self.__db_session.refresh(new_user)

        return User(
            id=new_user.id,
            auth_provider_id=new_user.auth_provider_id,
            name=new_user.name,
            avatar_url=new_user.avatar_url,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
        )

    @override
    async def update_user(self, user: User) -> User:
        update_user_smtm = select(UserTable).where(UserTable.id == user.id)

        update_user_result = await self.__db_session.execute(update_user_smtm)
        existing_user = update_user_result.scalar_one_or_none()

        if existing_user is None:
            raise UserNotFoundError(user_id=user.id)

        existing_user.name = user.name
        existing_user.avatar_url = user.avatar_url
        existing_user.updated_at = user.updated_at

        self.__db_session.add(existing_user)
        await self.__db_session.commit()
        await self.__db_session.refresh(existing_user)

        return User(
            id=existing_user.id,
            auth_provider_id=existing_user.auth_provider_id,
            name=existing_user.name,
            avatar_url=existing_user.avatar_url,
            created_at=existing_user.created_at,
            updated_at=existing_user.updated_at,
        )
