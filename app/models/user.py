"""
Модель таблицы users.

Центральная сущность: профиль биохакера с JSONB-полями
для пищевых предпочтений, фитнес-метрик и wearable-токенов.
"""

import enum

from sqlalchemy import BigInteger, Boolean, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class GenderEnum(str, enum.Enum):
    """Биологический пол пользователя."""

    MALE = "male"
    FEMALE = "female"


class ActivityLevelEnum(str, enum.Enum):
    """Уровень физической активности."""

    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class User(TimestampMixin, Base):
    """Таблица users — главный профиль пользователя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)

    # ── Onboarding & Policy ──
    has_accepted_policy: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # ── Geo & Timezone ──
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Moscow", server_default="Europe/Moscow")
    is_traveling: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # ── Anthropometry ──
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Activity & Goals ──
    activity_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    calories_goal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_ration_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Sleep ──
    baseline_sleep_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── JSONB fields (GIN-indexed) ──
    dietary_preferences: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    diseases: Mapped[str | None] = mapped_column(String(512), nullable=True)
    allergies: Mapped[str | None] = mapped_column(String(512), nullable=True)
    kitchen_equipment: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    fitness_equipment: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    fitness_capacity: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="baseline_rhr, vo2_max, lactate_threshold, mrv_sets, acwr_rolling, predicted_1rm, red_flags",
    )
    meal_schedule: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    water_preferences: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    wearable_tokens: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="Шифруется через MultiFernet (Application-Level Encryption)",
    )
    menstrual_cycle_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)

    # ── Completeness & Quotas ──
    data_completeness_score: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    daily_ai_requests: Mapped[int] = mapped_column(
        Integer,
        default=5,
        server_default="5",
        comment="Лимит списывается ТОЛЬКО при запуске Консилиума",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} tg={self.telegram_id}>"
