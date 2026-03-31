import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid7

from sqlalchemy import CHAR, Boolean, DateTime, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.models.base import Base

if TYPE_CHECKING:
    from .user_table import UserTable


class ApiKeyTable(Base):
    __tablename__ = "api_key"
    __table_args__ = {"schema": "auth"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    public_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    private_key_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("auth.user.id"), nullable=False, index=True)

    expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["UserTable"] = relationship(back_populates="api_keys", lazy="raise")
