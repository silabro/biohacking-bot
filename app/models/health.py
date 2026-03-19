"""
Модели здоровья: substance_interactions, supplements_log,
medications_log, ru_drugs_registry.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# ──────────────────────────────────────────────────────────────
# substance_interactions  (ATC Conflict Matrix)
# ──────────────────────────────────────────────────────────────

class SubstanceInteraction(Base):
    """Матрица взаимодействий субстанций (АТХ-коды)."""

    __tablename__ = "substance_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    atc_code_a: Mapped[str] = mapped_column(String(16), nullable=False, index=True, comment="Класс АТХ")
    atc_code_b: Mapped[str] = mapped_column(String(16), nullable=False, index=True, comment="Класс АТХ")
    interaction_type: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="CYP450_antagonist, absorption_blocker, etc.",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(32), nullable=True)


# ──────────────────────────────────────────────────────────────
# supplements_log
# ──────────────────────────────────────────────────────────────

class SupplementsLog(Base):
    """Лог приёма нутрицевтиков (БАДов)."""

    __tablename__ = "supplements_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    dosage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    circadian_anchor: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="Привязка к циркадному ритму",
    )
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )


# ──────────────────────────────────────────────────────────────
# medications_log
# ──────────────────────────────────────────────────────────────

class MedicationsLog(Base):
    """Лог приёма медикаментов."""

    __tablename__ = "medications_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    dosage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pharmacokinetics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)


# ──────────────────────────────────────────────────────────────
# ru_drugs_registry  (База ЕСКЛП)
# ──────────────────────────────────────────────────────────────

class RuDrugsRegistry(Base):
    """Реестр лекарственных средств РФ (ЕСКЛП). Заполняется офлайн-парсером CLI."""

    __tablename__ = "ru_drugs_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trade_name: Mapped[str] = mapped_column(
        String(512), nullable=False, index=True, comment="Торговое название",
    )
    inn: Mapped[str | None] = mapped_column(
        String(512), nullable=True, index=True, comment="МНН (Международное непатентованное название)",
    )
    atc_code: Mapped[str | None] = mapped_column(
        String(16), nullable=True, index=True, comment="Класс АТХ",
    )
