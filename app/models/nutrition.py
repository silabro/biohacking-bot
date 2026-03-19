"""
Модели нутрициологии: user_protocols, user_recipes, fridge_items.
"""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# ──────────────────────────────────────────────────────────────
# user_protocols
# ──────────────────────────────────────────────────────────────

class UserProtocol(Base):
    """Протоколы питания / фастинга пользователя."""

    __tablename__ = "user_protocols"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    goal: Mapped[str | None] = mapped_column(String(256), nullable=True)
    medical_constraints_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    active_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )


# ──────────────────────────────────────────────────────────────
# user_recipes  (Smart Chef Blindspot Fix)
# ──────────────────────────────────────────────────────────────

class UserRecipe(Base):
    """Пользовательские рецепты (включая Cheat Meals с is_estimated)."""

    __tablename__ = "user_recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    macros_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    ingredients_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_estimated: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false",
        comment="True для Cheat Meals (приблизительная оценка)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


# ──────────────────────────────────────────────────────────────
# fridge_items
# ──────────────────────────────────────────────────────────────

class FridgeUnitEnum(str, enum.Enum):
    """Допустимые единицы измерения продуктов."""

    GRAMS = "g"
    MILLILITERS = "ml"


class FridgeItem(Base):
    """Содержимое «Умного холодильника» пользователя."""

    __tablename__ = "fridge_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    proteins: Mapped[float | None] = mapped_column(Float, nullable=True)
    fats: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs: Mapped[float | None] = mapped_column(Float, nullable=True)
    fiber: Mapped[float | None] = mapped_column(Float, nullable=True)
    food_matrix_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    is_supplement: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_staple: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false",
        comment="Smart Pantry: бакалея, ИИ использует свободно, не списывается",
    )
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(
        String(8), nullable=True, comment="Enum: 'g' | 'ml'",
    )
    price_per_unit: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Moving Average",
    )
    price_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    is_expired: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false",
        comment="Hidden flag — скрытый признак просроченности",
    )
