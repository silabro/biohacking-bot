"""Базовый класс для всех SQLAlchemy-моделей."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Базовый DeclarativeBase.

    Все модели наследуются от этого класса, чтобы
    Alembic мог собрать единый metadata.
    """
