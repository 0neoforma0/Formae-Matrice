"""Titulaire — le compte qui écrit et valide. Un seul au MVP (identité nominative différée en V2)."""

import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class Titulaire(Base):
    __tablename__ = "titulaire"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_agence: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())
