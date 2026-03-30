from sqlalchemy.orm import DeclarativeBase

from app.core.env import settings


class Base(DeclarativeBase):
    metadata = DeclarativeBase.metadata
    __table_args__ = {"schema": settings.postgres_schema}
