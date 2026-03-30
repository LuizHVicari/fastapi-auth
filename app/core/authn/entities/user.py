import datetime
from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, slots=True)
class User:
    id: UUID
    auth_provider_id: str
    name: str
    avatar_url: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
