from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.env import settings

engine = create_async_engine(settings.postgres_url, echo=settings.db_echo)

_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with _session_factory() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_session)]
