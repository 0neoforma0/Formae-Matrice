"""
Version — historique append-only de l'Entrée.

Aucun UPDATE/DELETE au niveau applicatif (voir migration 0002 : REVOKE
sur le rôle applicatif). La portée (phase_id) est ici, pas sur l'Entrée.

Attributs JSONB par nature (décision d'origine) :
  Décision    — (aucun)
  Constat     — source_methode (optionnel)
  Contrainte  — niveau ('bloquante' | 'a_surveiller', obligatoire), entrees_impactees (array d'UUID)
  Jalon       — phase_declenchee (id phase, obligatoire)

Pièce justificative optionnelle (décision 11/08/2026) : une Version peut
n'avoir aucune pièce jointe, à la création comme plus tard.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

STATUTS_VERSION = ("Active", "Perimee")
PRECISIONS_DATE = ("exacte", "approximative")


class Version(Base):
    __tablename__ = "version"
    __table_args__ = (
        CheckConstraint(f"statut IN {STATUTS_VERSION}", name="ck_version_statut"),
        CheckConstraint(f"date_effective_precision IN {PRECISIONS_DATE}", name="ck_version_date_precision"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entree_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("entree.id"), nullable=False)

    valeur: Mapped[str] = mapped_column(String, nullable=False)
    phase_id: Mapped[int] = mapped_column(ForeignKey("phase.id"), nullable=False)

    date_effective: Mapped[date] = mapped_column(Date, nullable=False)
    date_effective_precision: Mapped[str] = mapped_column(String, nullable=False, default="exacte")

    declare_par_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("titulaire.id"), nullable=False)
    statut: Mapped[str] = mapped_column(String, nullable=False, default="Active")
    cloture: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    attributs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())

    entree: Mapped["Entree"] = relationship(  # noqa: F821
        "Entree",
        back_populates="versions",
        foreign_keys=[entree_id],
    )
