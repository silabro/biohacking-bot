"""
Асинхронный движок БД и фабрика сессий.

Правила (01_architecture_and_rules.md):
- NullPool СТРОГО ЗАПРЕЩЁН — используем стандартный пул (pool_size=20, max_overflow=10).
- AsyncEngine — Scope.APP (Dishka), AsyncSession — Scope.REQUEST.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    url=settings.database_url,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
