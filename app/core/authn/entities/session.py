import datetime
from dataclasses import dataclass
from uuid import UUID


@dataclass
class SessionIdentity:
    id: UUID
    traits: dict[str, str]


@dataclass
class Session:
    id: UUID
    active: bool
    expires_at: datetime.datetime
    identity: SessionIdentity
