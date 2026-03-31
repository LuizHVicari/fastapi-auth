from collections.abc import Callable, Coroutine
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.core.authn.dependencies import CurrentUser
from app.core.authz.adapters import KetAuthzProvider
from app.core.authz.ports import AuthzProvider
from app.core.authz.services import AuthzService


def get_authz_provider() -> AuthzProvider:
    return KetAuthzProvider()


AuthzProviderDep = Annotated[AuthzProvider, Depends(get_authz_provider)]


def get_authz_service(provider: AuthzProviderDep) -> AuthzService:
    return AuthzService(provider)


AuthzServiceDep = Annotated[AuthzService, Depends(get_authz_service)]


def verify_type_permission(
    relation: str | StrEnum, object_type: str | StrEnum
) -> Callable[..., Coroutine[None, None, None]]:
    """Return a FastAPI dependency that checks a type-level permission for the current user.

    Use in ``dependencies=[Depends(...)]`` on a router or endpoint.

    Args:
        relation: The relation to check (e.g. ``Relation.READER`` or ``"reader"``).
        object_type: The object type namespace (e.g. ``"documents"``).

    Raises:
        HTTPException: 403 if the current user does not have the required permission.

    Example::

        @router.get("/documents", dependencies=[Depends(verify_type_permission(Relation.READER, "documents"))])
        async def list_documents(): ...
    """

    async def _verify(current_user: CurrentUser, authz_service: AuthzServiceDep) -> None:
        allowed = await authz_service.check_type_permission(current_user.id, relation, object_type)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    return _verify


def verify_object_permission(
    relation: str | StrEnum, object_type: str | StrEnum
) -> Callable[..., Coroutine[None, None, None]]:
    """Return a FastAPI dependency that checks an instance-level permission for the current user.

    Reads the ``object_id`` from the path parameter of the same name.
    Use in ``dependencies=[Depends(...)]`` on a router or endpoint.

    Args:
        relation: The relation to check (e.g. ``Relation.READER`` or ``"reader"``).
        object_type: The object type namespace (e.g. ``"documents"``).

    Raises:
        HTTPException: 403 if the current user does not have the required permission
            on the specific object.

    Example::

        @router.get(
            "/documents/{object_id}",
            dependencies=[Depends(verify_object_permission(Relation.READER, "documents"))],
        )
        async def get_document(object_id: UUID): ...
    """

    async def _verify(
        object_id: UUID, current_user: CurrentUser, authz_service: AuthzServiceDep
    ) -> None:
        allowed = await authz_service.check_object_permission(
            current_user.id, relation, object_type, object_id
        )
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    return _verify
