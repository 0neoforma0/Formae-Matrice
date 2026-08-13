"""
Lien d'accès — nominatif, révocable. Modèle d'accès à deux niveaux :
titulaire écrit/valide, le reste consulte via ce lien scopé.

Expiration automatique (décision 11/08/2026, Lot 4) : 90 jours
d'inactivité (voir `settings.lien_acces_expiration_jours`). Toute
consultation réinitialise `date_derniere_consultation`. La révocation
manuelle reste possible à tout moment, indépendamment de ce délai.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base

STATUTS_LIEN = ("Actif", "Revoque")


class LienAcces(Base):
    __tablename__ = "lien_acces"
    __table_args__ = (
        CheckConstraint(f"statut IN {STATUTS_LIEN}", name="ck_lien_acces_statut"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    projet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projet.id"), nullable=False)
    intervenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("intervenant.id"), nullable=False)

    token: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    statut: Mapped[str] = mapped_column(String, nullable=False, default="Actif")
    voir_sensible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())
    date_revocation: Mapped[datetime | None] = mapped_column(nullable=True)

    # Décision 11/08/2026 — support de l'expiration à 90 jours d'inactivité.
    date_derniere_consultation: Mapped[datetime | None] = mapped_column(nullable=True)
