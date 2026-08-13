"""Intervenant — répertoire d'agence, réutilisable entre projets."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class Intervenant(Base):
    __tablename__ = "intervenant"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulaire_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("titulaire.id"), nullable=False)
    nom: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    entreprise: Mapped[str | None] = mapped_column(String, nullable=True)
    contact: Mapped[str | None] = mapped_column(String, nullable=True)
    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())
