import datetime
from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class SessionIdentity:
    id: UUID
    traits: dict[str, str]


@dataclass(slots=True, kw_only=True)
class Session:
    id: UUID
    active: bool
    expires_at: datetime.datetime
    identity: SessionIdentity
