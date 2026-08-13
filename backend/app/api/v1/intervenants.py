import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.intervenant import Intervenant
from app.models.titulaire import Titulaire
from app.schemas.intervenant import IntervenantCreation, IntervenantLecture, IntervenantMaJ

router = APIRouter(prefix="/intervenants", tags=["intervenants"])


def _titulaire_unique(db: Session) -> Titulaire:
    """Au MVP il n'y a qu'un seul titulaire (voir app/api/v1/entrees.py)."""
    titulaire = db.query(Titulaire).first()
    if titulaire is None:
        raise HTTPException(
            412,
            "Aucun titulaire enregistré — créer le compte agence avant tout Intervenant.",
        )
    return titulaire


@router.post("", response_model=IntervenantLecture, status_code=201)
def creer_intervenant(payload: IntervenantCreation, db: Session = Depends(get_db)) -> Intervenant:
    """Répertoire d'agence — un Intervenant n'est pas rattaché à un Projet, réutilisable entre eux."""
    titulaire = _titulaire_unique(db)
    intervenant = Intervenant(titulaire_id=titulaire.id, **payload.model_dump())
    db.add(intervenant)
    db.commit()
    db.refresh(intervenant)
    return intervenant


@router.get("", response_model=list[IntervenantLecture])
def lister_intervenants(db: Session = Depends(get_db)) -> list[Intervenant]:
    return db.query(Intervenant).order_by(Intervenant.nom).all()


@router.get("/{intervenant_id}", response_model=IntervenantLecture)
def lire_intervenant(intervenant_id: uuid.UUID, db: Session = Depends(get_db)) -> Intervenant:
    intervenant = db.get(Intervenant, intervenant_id)
    if intervenant is None:
        raise HTTPException(404, "Intervenant introuvable.")
    return intervenant


@router.patch("/{intervenant_id}", response_model=IntervenantLecture)
def modifier_intervenant(
    intervenant_id: uuid.UUID, payload: IntervenantMaJ, db: Session = Depends(get_db)
) -> Intervenant:
    intervenant = db.get(Intervenant, intervenant_id)
    if intervenant is None:
        raise HTTPException(404, "Intervenant introuvable.")

    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(intervenant, champ, valeur)

    db.commit()
    db.refresh(intervenant)
    return intervenant


@router.delete("/{intervenant_id}", status_code=204)
def supprimer_intervenant(intervenant_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    intervenant = db.get(Intervenant, intervenant_id)
    if intervenant is None:
        raise HTTPException(404, "Intervenant introuvable.")

    db.delete(intervenant)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            409,
            "Cet Intervenant est encore rattaché à des Entrées ou des liens d'accès — impossible de le supprimer.",
        ) from exc
