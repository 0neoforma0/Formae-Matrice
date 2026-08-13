import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IntervenantCreation(BaseModel):
    nom: str
    role: str | None = None
    entreprise: str | None = None
    contact: str | None = None


class IntervenantMaJ(BaseModel):
    """Mise à jour partielle — seuls les champs fournis sont modifiés."""

    nom: str | None = None
    role: str | None = None
    entreprise: str | None = None
    contact: str | None = None


class IntervenantLecture(BaseModel):
    id: uuid.UUID
    titulaire_id: uuid.UUID
    nom: str
    role: str | None
    entreprise: str | None
    contact: str | None
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)
