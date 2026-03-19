"""
Переиспользуемые миксины для SQLAlchemy-моделей.

TimestampMixin — добавляет поле last_active_at (TIMESTAMP WITH TIME ZONE).
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Миксин с полем last_active_at (UTC, timezone-aware)."""

    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
