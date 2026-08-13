"""Consultation — journal d'accès, append-only (aucun UPDATE/DELETE applicatif)."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base

TYPES_RESSOURCE = ("Entree", "Piece", "Projet")


class Consultation(Base):
    __tablename__ = "consultation"
    __table_args__ = (
        CheckConstraint(f"ressource_type IN {TYPES_RESSOURCE}", name="ck_consultation_ressource_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lien_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lien_acces.id"), nullable=False)
    ressource_type: Mapped[str] = mapped_column(String, nullable=False)
    ressource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    date_consultation: Mapped[datetime] = mapped_column(server_default=func.now())
