from app.core.authn.entities import User
from app.core.authn.errors import UserAlreadyExistsError, UserNotFoundError
from app.core.authn.ports import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.__user_repository = user_repository

    async def get_user_by_auth_provider_id(self, auth_provider_id: str) -> User | None:
        user = await self.__user_repository.find_user_by_auth_provider_id(auth_provider_id)

        return user

    async def create_user(self, user: User) -> User:
        existing = await self.__user_repository.find_user_by_auth_provider_id(user.auth_provider_id)

        if existing is not None:
            raise UserAlreadyExistsError(auth_provider_id=user.auth_provider_id)

        return await self.__user_repository.create_user(user)

    async def update_user(self, user: User) -> User:
        existing = await self.__user_repository.find_user_by_id(user.id)

        if existing is None:
            raise UserNotFoundError(user_id=user.id)

        return await self.__user_repository.update_user(user)
