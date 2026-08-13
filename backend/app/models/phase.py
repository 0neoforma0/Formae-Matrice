"""Phase — table de référence, volontairement extensible (jamais figée en dur dans le code)."""

from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Phase(Base):
    __tablename__ = "phase"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    ordre: Mapped[int] = mapped_column(SmallInteger, nullable=False)


# Valeurs de départ — insérées par la migration 0001, jamais codées en dur ailleurs.
PHASES_INITIALES = [
    {"id": 1, "code": "Faisabilite", "ordre": 1},
    {"id": 2, "code": "Conception", "ordre": 2},
    {"id": 3, "code": "Consultation", "ordre": 3},
    {"id": 4, "code": "Chantier", "ordre": 4},
    {"id": 5, "code": "Reception", "ordre": 5},
]
