import hashlib
import secrets
from typing import Literal, NamedTuple

from loguru import logger

from app.core.api_keys.entities import ApiKey
from app.core.api_keys.errors import ApiKeyNotFoundError
from app.core.api_keys.errors.invalid_api_key_format_error import InvalidApiKeyFormatError
from app.core.api_keys.ports import ApiKeyRepository
from app.core.authn.entities import User
from app.utils.pagination_utils import Paginated
from app.utils.time_utils import add_days_to_date, now_utc


class SplittedKeyString(NamedTuple):
    public_key: str
    private_key: str


class ApiKeyService:
    def __init__(self, api_key_repository: ApiKeyRepository) -> None:
        self.__api_key_repository = api_key_repository

    async def generate_api_key(
        self, *, user: User, description: str | None, duration_days: int
    ) -> str:
        public_key = secrets.token_urlsafe(32)
        private_key = secrets.token_urlsafe(64)
        private_key_hash = hashlib.sha256(private_key.encode()).hexdigest()

        logger.info(
            f"Generating API key for user {user.id} with description '{description}' and duration of {duration_days} days"
        )

        api_key = ApiKey(
            public_key=public_key,
            secret_hash=private_key_hash,
            description=description,
            is_revoked=False,
            expires_at=add_days_to_date(now_utc(), max(1, duration_days)),
            user_id=user.id,
        )
        await self.__api_key_repository.create_api_key(api_key)

        logger.info(f"API key generated for user {user.id} with description '{description}'")

        return self.__create_key_string(public_key, private_key)

    async def list_user_api_keys(
        self,
        *,
        user: User,
        expired: bool | None = None,
        description: str | None = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Literal["created_at", "updated_at", "description", "user_id"] = "created_at",
        order_direction: Literal["asc", "desc"] = "asc",
    ) -> Paginated[ApiKey]:
        return await self.__api_key_repository.list_api_keys(
            user_id=user.id,
            expired=expired,
            description=description,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_direction=order_direction,
        )

    async def revoke_api_key(self, *, user: User, public_key: str) -> None:
        api_key = await self.__api_key_repository.find_api_key_by_public_key(public_key)
        if api_key is None or api_key.user_id != user.id:
            logger.warning(
                f"User {user.id} attempted to revoke non-existent or unauthorized API key with public key {public_key}"
            )
            raise ApiKeyNotFoundError(public_key=public_key)

        api_key.is_revoked = True
        await self.__api_key_repository.update_api_key(api_key)

        logger.info(f"API key with public key {public_key} has been revoked")

    async def validate_api_key(self, key_string: str) -> ApiKey:
        spllited_key = self.__split_key_string(key_string)

        api_key = await self.__api_key_repository.find_api_key_by_public_key(
            spllited_key.public_key
        )
        secret_hash = hashlib.sha256(spllited_key.private_key.encode()).hexdigest()
        if api_key is None or api_key.secret_hash != secret_hash:
            logger.warning(f"Invalid API key attempt with public key {spllited_key.public_key}")
            raise ApiKeyNotFoundError(public_key=spllited_key.public_key)

        return api_key

    def __create_key_string(self, public_key: str, private_key: str) -> str:
        return f"{public_key}:{private_key}"

    def __split_key_string(self, key_string: str) -> SplittedKeyString:
        try:
            public_key, private_key = key_string.split(":")
            return SplittedKeyString(public_key=public_key, private_key=private_key)
        except ValueError as e:
            logger.error(f"Failed to split API key string: {e}")
            raise InvalidApiKeyFormatError() from e
