import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class VersionCreation(BaseModel):
    valeur: str
    phase_id: int
    date_effective: date
    date_effective_precision: str = "exacte"
    attributs: dict = Field(default_factory=dict)
    piece_ids: list[uuid.UUID] = Field(default_factory=list)  # optionnel (décision 11/08/2026)
    cloture: bool = False  # true → l'Entrée passe au statut Perimee (append-only, jamais un UPDATE)


class EntreeCreation(BaseModel):
    projet_id: uuid.UUID
    nature: str
    version_initiale: VersionCreation
    axe_ids: list[uuid.UUID] = Field(default_factory=list)
    intervenant_ids: list[uuid.UUID] = Field(default_factory=list)
    sensible: bool = False  # marquage manuel — combiné en OR avec l'héritage des axes
    phase_alerte_id: int | None = None  # pense-bête, non bloquant


class VersionLecture(BaseModel):
    id: uuid.UUID
    valeur: str
    phase_id: int
    date_effective: date
    statut: str
    cloture: bool
    attributs: dict
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)


class EntreeLecture(BaseModel):
    id: uuid.UUID
    projet_id: uuid.UUID
    code_lecture: str
    nature: str
    statut: str
    sensible: bool
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)
