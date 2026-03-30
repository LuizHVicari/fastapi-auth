from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class Relation(StrEnum):
    """Built-in relations. Extend or replace with domain-specific StrEnums."""

    READER = "reader"
    WRITER = "writer"
    OWNER = "owner"


@dataclass(frozen=True)
class TypePermission:
    """Permission granted on all objects of a given type.

    Example:
        TypePermission(subject_id=user_id, relation=Relation.READER, object_type="documents")
        Means: user can read all documents.
    """

    subject_id: UUID
    relation: str
    object_type: str


@dataclass(frozen=True)
class ObjectPermission:
    """Permission granted on a specific object instance.

    Example:
        ObjectPermission(subject_id=user_id, relation=Relation.READER, object_type="documents", object_id=doc_id)
        Means: user can read that specific document.
    """

    subject_id: UUID
    relation: str
    object_type: str
    object_id: UUID
