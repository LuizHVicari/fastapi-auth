import datetime
from dataclasses import dataclass, field
from uuid import UUID, uuid7

from app.utils.time_utils import now_utc


@dataclass(kw_only=True, slots=True)
class ApiKey:
    id: UUID = field(default_factory=uuid7)
    public_key: str
    secret_hash: str
    description: str | None = None
    user_id: UUID

    expires_at: datetime.datetime | None = None
    is_revoked: bool = False

    created_at: datetime.datetime = field(default_factory=now_utc)
    updated_at: datetime.datetime = field(default_factory=now_utc)

    @property
    def can_be_used(self) -> bool:
        if self.is_revoked:
            return False
        return not (self.expires_at and self.expires_at < now_utc())
