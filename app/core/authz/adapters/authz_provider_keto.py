from enum import StrEnum
from typing import override
from uuid import UUID

import httpx

from app.core.authz.ports import AuthzProvider
from app.core.env import settings


def _object_str(object_type: str | StrEnum, object_id: UUID | None) -> str:
    if object_id is None:
        return str(object_type)
    return f"{object_type}:{object_id}"


class KetAuthzProvider(AuthzProvider):
    """Ory Keto implementation of AuthzProvider using the REST API."""

    @override
    async def check_type_permission(
        self, subject_id: UUID, relation: str | StrEnum, object_type: str | StrEnum
    ) -> bool:
        """Check if a subject has a relation on all objects of a given type.

        Translates to a Keto check on namespace=object_type, object=object_type,
        relation=relation, subject=user:<subject_id>.

        Example:
            >>> await provider.check_type_permission(user_id, Relation.READER, "documents")
        """
        return await self.__check(subject_id, relation, object_type, None)

    @override
    async def check_object_permission(
        self,
        subject_id: UUID,
        relation: str | StrEnum,
        object_type: str | StrEnum,
        object_id: UUID,
    ) -> bool:
        """Check if a subject has a relation on a specific object instance.

        Translates to a Keto check on namespace=object_type, object=object_type:object_id,
        relation=relation, subject=user:<subject_id>.

        Example:
            >>> await provider.check_object_permission(
            ...     user_id, Relation.READER, "documents", doc_id
            ... )
        """
        return await self.__check(subject_id, relation, object_type, object_id)

    @override
    async def grant_type_permission(
        self, subject_id: UUID, relation: str | StrEnum, object_type: str | StrEnum
    ) -> None:
        """Grant a subject a relation on all objects of a given type.

        Example:
            >>> await provider.grant_type_permission(user_id, Relation.WRITER, "documents")
        """
        await self.__write(subject_id, relation, object_type, None)

    @override
    async def grant_object_permission(
        self,
        subject_id: UUID,
        relation: str | StrEnum,
        object_type: str | StrEnum,
        object_id: UUID,
    ) -> None:
        """Grant a subject a relation on a specific object instance.

        Example:
            >>> await provider.grant_object_permission(user_id, Relation.OWNER, "documents", doc_id)
        """
        await self.__write(subject_id, relation, object_type, object_id)

    @override
    async def revoke_type_permission(
        self, subject_id: UUID, relation: str | StrEnum, object_type: str | StrEnum
    ) -> None:
        """Revoke a subject's relation on all objects of a given type.

        Example:
            >>> await provider.revoke_type_permission(user_id, Relation.READER, "documents")
        """
        await self.__delete(subject_id, relation, object_type, None)

    @override
    async def revoke_object_permission(
        self,
        subject_id: UUID,
        relation: str | StrEnum,
        object_type: str | StrEnum,
        object_id: UUID,
    ) -> None:
        """Revoke a subject's relation on a specific object instance.

        Example:
            >>> await provider.revoke_object_permission(
            ...     user_id, Relation.OWNER, "documents", doc_id
            ... )
        """
        await self.__delete(subject_id, relation, object_type, object_id)

    async def __check(
        self,
        subject_id: UUID,
        relation: str | StrEnum,
        object_type: str | StrEnum,
        object_id: UUID | None,
    ) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.keto_read_url}/relation-tuples/check",
                params={
                    "namespace": str(object_type),
                    "object": _object_str(object_type, object_id),
                    "relation": str(relation),
                    "subject_id": str(subject_id),
                },
            )
        return response.is_success and response.json().get("allowed", False)

    async def __write(
        self,
        subject_id: UUID,
        relation: str | StrEnum,
        object_type: str | StrEnum,
        object_id: UUID | None,
    ) -> None:
        async with httpx.AsyncClient() as client:
            await client.put(
                f"{settings.keto_write_url}/relation-tuples",
                json={
                    "namespace": str(object_type),
                    "object": _object_str(object_type, object_id),
                    "relation": str(relation),
                    "subject_id": str(subject_id),
                },
            )

    async def __delete(
        self,
        subject_id: UUID,
        relation: str | StrEnum,
        object_type: str | StrEnum,
        object_id: UUID | None,
    ) -> None:
        async with httpx.AsyncClient() as client:
            await client.delete(
                f"{settings.keto_write_url}/relation-tuples",
                params={
                    "namespace": str(object_type),
                    "object": _object_str(object_type, object_id),
                    "relation": str(relation),
                    "subject_id": str(subject_id),
                },
            )
