"""
Axe de classement — Lot / Ouvrage / Localisation. Table générique unique, discriminée par type.

Implémentation provisoire dans Matrice (décision 11/08/2026) — sera extraite
vers un service de socle commun Formae à l'ouverture du développement de Prisme.

Champ `sensible` ajouté le 11/08/2026 : un axe marqué sensible rend
automatiquement sensibles toutes les Entrées qui lui sont rattachées
(voir modèle Entrée — sensibilité héritée + marquage manuel cumulatifs).
"""

import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

TYPES_AXE = ("Lot", "Ouvrage", "Localisation")


class AxeClassement(Base):
    __tablename__ = "axe_classement"
    __table_args__ = (
        CheckConstraint(f"type IN {TYPES_AXE}", name="ck_axe_classement_type"),
        UniqueConstraint("projet_id", "type", "valeur", name="uq_axe_classement_projet_type_valeur"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    projet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projet.id"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    valeur: Mapped[str] = mapped_column(String, nullable=False)

    # Décision 11/08/2026 — un axe marqué sensible rend sensibles les Entrées rattachées.
    sensible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
