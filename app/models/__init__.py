"""
Центральный реестр всех SQLAlchemy-моделей.

Импорт Base + каждой модели гарантирует, что Alembic
обнаружит все таблицы через Base.metadata.
"""

from app.models.base import Base
from app.models.health import (
    MedicationsLog,
    RuDrugsRegistry,
    SubstanceInteraction,
    SupplementsLog,
)
from app.models.logs import (
    BiomarkerLog,
    LifestyleLog,
    SymptomLog,
    WorkoutLog,
)
from app.models.nutrition import FridgeItem, UserProtocol, UserRecipe
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "UserProtocol",
    "UserRecipe",
    "FridgeItem",
    "SubstanceInteraction",
    "SupplementsLog",
    "MedicationsLog",
    "SymptomLog",
    "LifestyleLog",
    "WorkoutLog",
    "BiomarkerLog",
    "RuDrugsRegistry",
]
