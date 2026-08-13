"""
Pièce justificative — copiée, jamais un simple pointeur externe.

Décision 11/08/2026 : format PDF uniquement à l'import (Lot 5). Un
document bureautique doit être exporté en PDF avant rattachement.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base

ORIGINES_PIECE = ("import_pilotis", "depot_direct")


class PieceJustificative(Base):
    __tablename__ = "piece_justificative"
    __table_args__ = (
        CheckConstraint(f"origine IN {ORIGINES_PIECE}", name="ck_piece_origine"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String, nullable=False)  # CR chantier / PV / plan / photo / rapport / autre
    date_diffusion: Mapped[date] = mapped_column(Date, nullable=False)
    origine: Mapped[str] = mapped_column(String, nullable=False)

    fichier_url: Mapped[str] = mapped_column(String, nullable=False)  # Scaleway Object Storage
    reference_externe: Mapped[str | None] = mapped_column(String, nullable=True)  # lien Pilotis d'origine

    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())
