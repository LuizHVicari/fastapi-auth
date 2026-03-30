from enum import StrEnum
from typing import Protocol
from uuid import UUID


class AuthzProvider(Protocol):
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
            >>> await provider.check_type_permission(user_id, Relation.READER, "documents")
        """
        ...

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
            >>> await provider.check_object_permission(user_id, Relation.READER, "documents", doc_id)
        """
        ...

    async def grant_type_permission(
        self, subject_id: UUID, relation: str | StrEnum, object_type: str | StrEnum
    ) -> None:
        """Grant a subject a relation on all objects of a given type.

        Args:
            subject_id: The UUID of the subject (e.g. a user).
            relation: The relation to grant (e.g. ``Relation.WRITER`` or ``"writer"``).
            object_type: The object type namespace (e.g. ``"documents"``).

        Example:
            >>> await provider.grant_type_permission(user_id, Relation.WRITER, "documents")
        """
        ...

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
            >>> await provider.grant_object_permission(user_id, Relation.OWNER, "documents", doc_id)
        """
        ...

    async def revoke_type_permission(
        self, subject_id: UUID, relation: str | StrEnum, object_type: str | StrEnum
    ) -> None:
        """Revoke a subject's relation on all objects of a given type.

        Args:
            subject_id: The UUID of the subject (e.g. a user).
            relation: The relation to revoke (e.g. ``Relation.READER`` or ``"reader"``).
            object_type: The object type namespace (e.g. ``"documents"``).

        Example:
            >>> await provider.revoke_type_permission(user_id, Relation.READER, "documents")
        """
        ...

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
            >>> await provider.revoke_object_permission(user_id, Relation.OWNER, "documents", doc_id)
        """
        ...
