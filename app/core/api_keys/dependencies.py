from typing import Annotated

from fastapi import Depends

from app.core.api_keys.adapters import ApiKeyRepositorySql
from app.core.api_keys.ports import ApiKeyRepository
from app.core.api_keys.services import ApiKeyService
from app.core.database.engine import DbSession


def get_api_key_repository(db_session: DbSession) -> ApiKeyRepository:
    return ApiKeyRepositorySql(db_session)


ApiKeyRepositoryDep = Annotated[ApiKeyRepository, Depends(get_api_key_repository)]


def get_api_key_service(api_key_repository: ApiKeyRepositoryDep) -> ApiKeyService:
    return ApiKeyService(api_key_repository)


ApiKeyServiceDep = Annotated[ApiKeyService, Depends(get_api_key_service)]
