import uuid

from pydantic import BaseModel, ConfigDict


class AxeClassementCreation(BaseModel):
    projet_id: uuid.UUID
    type: str  # Lot | Ouvrage | Localisation
    valeur: str
    sensible: bool = False


class AxeClassementMaJ(BaseModel):
    """Mise à jour partielle — seuls les champs fournis sont modifiés."""

    valeur: str | None = None
    sensible: bool | None = None


class AxeClassementLecture(BaseModel):
    id: uuid.UUID
    projet_id: uuid.UUID
    type: str
    valeur: str
    sensible: bool

    model_config = ConfigDict(from_attributes=True)
