from enum import StrEnum
from uuid import UUID

from app.core.authz.ports import AuthzProvider


class AuthzService:
    """Service for checking and managing authorization permissions.

    All Keto/provider details are hidden behind AuthzProvider — nothing
    from the authorization infrastructure leaks beyond this class.

    Usage:
        Inject AuthzService via FastAPI dependencies and use it in routers
        or other services. Never import the adapter directly outside of the
        composition root (dependencies.py).

    Example::

        service = AuthzService(provider)

        # Grant and check a type-level permission
        await service.grant_type_permission(user_id, Relation.READER, "documents")
        allowed = await service.check_type_permission(user_id, Relation.READER, "documents")

        # Grant and check an instance-level permission
        await service.grant_object_permission(user_id, Relation.OWNER, "documents", doc_id)
        allowed = await service.check_object_permission(user_id, Relation.OWNER, "documents", doc_id)
    """

    def __init__(self, provider: AuthzProvider) -> None:
        self.__provider = provider

    async def check_type_permission(
        self, subject_id: UUID, relation: str | StrEnum, object_type: str | StrEnum
    ) -> bool:
        """Check if a subject has a relation on all objects of a given type.

        Args:
            subject_id: The UUID of the subject (e.g. a user).
            relation: The relation to check (e.g. ``Relation.READER`` or ``"reader"``).
            object_type: The object type namespace (e.g. ``"documents"``).

        Returns:
            True if the permission exists, False otherwise.

        Example:
            >>> allowed = await service.check_type_permission(user_id, Relation.READER, "documents")
        """
        return await self.__provider.check_type_permission(subject_id, relation, object_type)

    async def check_object_permission(
        self,
        subject_id: UUID,
        relation: str | StrEnum,
        object_type: str | StrEnum,
        object_id: UUID,
    ) -> bool:
        """Check if a subject has a relation on a specific object instance.

        Args:
            subject_id: The UUID of the subject (e.g. a user).
            relation: The relation to check (e.g. ``Relation.READER`` or ``"reader"``).
            object_type: The object type namespace (e.g. ``"documents"``).
            object_id: The UUID of the specific object instance.

        Returns:
            True if the permission exists, False otherwise.

        Example:
            >>> allowed = await service.check_object_permission(user_id, Relation.READER, "documents", doc_id)
        """
        return await self.__provider.check_object_permission(subject_id, relation, object_type, object_id)

    async def grant_type_permission(
        self, subject_id: UUID, relation: str | StrEnum, object_type: str | StrEnum
    ) -> None:
        """Grant a subject a relation on all objects of a given type.

        Args:
            subject_id: The UUID of the subject (e.g. a user).
            relation: The relation to grant (e.g. ``Relation.WRITER`` or ``"writer"``).
            object_type: The object type namespace (e.g. ``"documents"``).

        Example:
            >>> await service.grant_type_permission(user_id, Relation.WRITER, "documents")
        """
        await self.__provider.grant_type_permission(subject_id, relation, object_type)

    async def grant_object_permission(
        self,
        subject_id: UUID,
        relation: str | StrEnum,
        object_type: str | StrEnum,
        object_id: UUID,
    ) -> None:
        """Grant a subject a relation on a specific object instance.

        Args:
            subject_id: The UUID of the subject (e.g. a user).
            relation: The relation to grant (e.g. ``Relation.OWNER`` or ``"owner"``).
            object_type: The object type namespace (e.g. ``"documents"``).
            object_id: The UUID of the specific object instance.

        Example:
            >>> await service.grant_object_permission(user_id, Relation.OWNER, "documents", doc_id)
        """
        await self.__provider.grant_object_permission(subject_id, relation, object_type, object_id)

    async def revoke_type_permission(
        self, subject_id: UUID, relation: str | StrEnum, object_type: str | StrEnum
    ) -> None:
        """Revoke a subject's relation on all objects of a given type.

        Args:
            subject_id: The UUID of the subject (e.g. a user).
            relation: The relation to revoke (e.g. ``Relation.READER`` or ``"reader"``).
            object_type: The object type namespace (e.g. ``"documents"``).

        Example:
            >>> await service.revoke_type_permission(user_id, Relation.READER, "documents")
        """
        await self.__provider.revoke_type_permission(subject_id, relation, object_type)

    async def revoke_object_permission(
        self,
        subject_id: UUID,
        relation: str | StrEnum,
        object_type: str | StrEnum,
        object_id: UUID,
    ) -> None:
        """Revoke a subject's relation on a specific object instance.

        Args:
            subject_id: The UUID of the subject (e.g. a user).
            relation: The relation to revoke (e.g. ``Relation.OWNER`` or ``"owner"``).
            object_type: The object type namespace (e.g. ``"documents"``).
            object_id: The UUID of the specific object instance.

        Example:
            >>> await service.revoke_object_permission(user_id, Relation.OWNER, "documents", doc_id)
        """
        await self.__provider.revoke_object_permission(subject_id, relation, object_type, object_id)
