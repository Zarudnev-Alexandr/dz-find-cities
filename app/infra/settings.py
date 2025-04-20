import os
from asyncio import current_task
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)

async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

scoped_session = async_scoped_session(async_session_maker, scopefunc=current_task)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
