from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid7

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .api_key_table import ApiKeyTable


class UserTable(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "auth"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    auth_provider_id: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    avatar_url: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    api_keys: Mapped[list["ApiKeyTable"]] = relationship(back_populates="user", lazy="raise")
