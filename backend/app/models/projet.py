"""Projet — porte la phase courante, maintenue via les Entrées de nature Jalon."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class Projet(Base):
    __tablename__ = "projet"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulaire_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("titulaire.id"), nullable=False)
    nom: Mapped[str] = mapped_column(String, nullable=False)
    typologie: Mapped[str | None] = mapped_column(String, nullable=True)  # pas d'enum figé
    phase_courante_id: Mapped[int | None] = mapped_column(SmallInteger, ForeignKey("phase.id"), nullable=True)

    # Séquence pour code_lecture de l'Entrée (ex. PROJ-0001).
    dernier_numero_entree: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Affichage seul — jamais un état technique.
    en_avant_plan: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())
