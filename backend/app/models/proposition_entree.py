"""
Proposition d'Entrée — objet créé le 10/08/2026 (Contrat de compatibilité intersystèmes, F-05).

Prisme et Pilotis n'ont pas d'Entrées : ils émettent un objet candidat que
seule Matrice matérialise en Entrée. Cela préserve l'Article 5 de la
Constitution Matrice — Matrice seule décide de ce qui entre chez elle.

Lot 2 (+10h dans la réestimation du 11/08/2026) : logique de
matérialisation. Seul le titulaire peut matérialiser (modèle d'accès à
deux niveaux — titulaire écrit/valide, le reste consulte).
"""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.entree import NATURES_ENTREE

SOURCES_PROPOSITION = ("Prisme", "Pilotis", "Interne")
STATUTS_PROPOSITION = ("En_attente", "Materialisee", "Rejetee")


class PropositionEntree(Base):
    __tablename__ = "proposition_entree"
    __table_args__ = (
        CheckConstraint(f"nature_proposee IN {NATURES_ENTREE}", name="ck_proposition_nature"),
        CheckConstraint(f"source IN {SOURCES_PROPOSITION}", name="ck_proposition_source"),
        CheckConstraint(f"statut IN {STATUTS_PROPOSITION}", name="ck_proposition_statut"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    projet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projet.id"), nullable=False)

    source: Mapped[str] = mapped_column(String, nullable=False)
    nature_proposee: Mapped[str] = mapped_column(String, nullable=False)
    contenu_propose: Mapped[str] = mapped_column(Text, nullable=False)
    attributs_proposes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    statut: Mapped[str] = mapped_column(String, nullable=False, default="En_attente")

    # Renseigné uniquement au moment de la matérialisation (jamais avant).
    entree_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("entree.id"), nullable=True)
    materialisee_par_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("titulaire.id"), nullable=True)

    date_proposition: Mapped[datetime] = mapped_column(server_default=func.now())
    date_traitement: Mapped[datetime | None] = mapped_column(nullable=True)
