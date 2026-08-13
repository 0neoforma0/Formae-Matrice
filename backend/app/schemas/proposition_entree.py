import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PropositionEntreeCreation(BaseModel):
    projet_id: uuid.UUID
    source: str  # Prisme | Pilotis | Interne
    nature_proposee: str
    contenu_propose: str
    attributs_proposes: dict = Field(default_factory=dict)


class PropositionEntreeLecture(BaseModel):
    id: uuid.UUID
    projet_id: uuid.UUID
    source: str
    nature_proposee: str
    contenu_propose: str
    statut: str
    entree_id: uuid.UUID | None
    date_proposition: datetime
    date_traitement: datetime | None

    model_config = ConfigDict(from_attributes=True)


class PropositionMaterialisation(BaseModel):
    """Le titulaire matérialise (ou rejette) une proposition. Lui seul peut le faire —
    modèle d'accès à deux niveaux, préserve l'Article 5 de la Constitution Matrice."""

    accepter: bool
    phase_id: int | None = None  # requis si accepter=True
    date_effective: str | None = None  # ISO date, requis si accepter=True
