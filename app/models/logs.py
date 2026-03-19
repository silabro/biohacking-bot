"""
Модели дневников/логов: symptom_logs, lifestyle_logs,
workouts_log, biomarker_logs.

Все таблицы логов имеют композитный индекс (user_id, date/timestamp)
для быстрых выборок по пользователю и дате.
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, Integer, String, Boolean, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# ──────────────────────────────────────────────────────────────
# symptom_logs
# ──────────────────────────────────────────────────────────────

class SymptomLog(Base):
    """Лог симптомов (интенсивность, категория боли, сытость)."""

    __tablename__ = "symptom_logs"
    __table_args__ = (
        Index("ix_symptom_logs_user_ts", "user_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    symptom_name: Mapped[str] = mapped_column(String(256), nullable=False)
    intensity: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="1-10")
    pain_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    satiety_level: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="1-10")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


# ──────────────────────────────────────────────────────────────
# lifestyle_logs  (Вместо water_logs)
# ──────────────────────────────────────────────────────────────

class LifestyleLog(Base):
    """Лог образа жизни: вода, электролиты, свет, термальный стресс, NEAT."""

    __tablename__ = "lifestyle_logs"
    __table_args__ = (
        Index("ix_lifestyle_logs_user_ts", "user_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    water_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    electrolytes: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    light_exposure: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="lux / spectrum",
    )
    thermal_stress: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="sauna / ice",
    )
    cognitive_load_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    movement_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="NEAT / Activity Snacks для Ramp-Up Protocol; НЕ попадает в workouts_log",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


# ──────────────────────────────────────────────────────────────
# workouts_log
# ──────────────────────────────────────────────────────────────

class WorkoutLog(Base):
    """Лог тренировок с JSONB-полями для планов и фактического выполнения."""

    __tablename__ = "workouts_log"
    __table_args__ = (
        Index("ix_workouts_log_user_date", "user_id", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    workout_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stress_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    planned_workout: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    actual_workout: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    recovery_interventions: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    training_effect: Mapped[float | None] = mapped_column(Float, nullable=True)
    training_load: Mapped[float | None] = mapped_column(Float, nullable=True)
    recovery_time_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)


# ──────────────────────────────────────────────────────────────
# biomarker_logs
# ──────────────────────────────────────────────────────────────

class BiomarkerLog(Base):
    """Лог биомаркеров (анализы крови и т.п.)."""

    __tablename__ = "biomarker_logs"
    __table_args__ = (
        Index("ix_biomarker_logs_user_date", "user_id", "date_tested"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    biomarker_name: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    reference_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    reference_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    date_tested: Mapped[date] = mapped_column(Date, nullable=False)
