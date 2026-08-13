import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.axe_classement import TYPES_AXE, AxeClassement
from app.models.projet import Projet
from app.schemas.axe_classement import AxeClassementCreation, AxeClassementLecture, AxeClassementMaJ

router = APIRouter(prefix="/axes", tags=["axes"])


@router.post("", response_model=AxeClassementLecture, status_code=201)
def creer_axe(payload: AxeClassementCreation, db: Session = Depends(get_db)) -> AxeClassement:
    """
    Un axe marqué `sensible` rend automatiquement sensibles les Entrées
    qui lui seront rattachées (héritage — voir modèle Entrée, Lot 2).
    """
    if payload.type not in TYPES_AXE:
        raise HTTPException(422, f"Type d'axe inconnu : {payload.type!r} (attendu parmi {TYPES_AXE}).")

    projet = db.get(Projet, payload.projet_id)
    if projet is None:
        raise HTTPException(404, "Projet introuvable.")

    axe = AxeClassement(**payload.model_dump())
    db.add(axe)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Un axe de ce type et cette valeur existe déjà pour ce Projet.") from exc
    db.refresh(axe)
    return axe


@router.get("", response_model=list[AxeClassementLecture])
def lister_axes(
    projet_id: uuid.UUID | None = None,
    type: str | None = None,
    db: Session = Depends(get_db),
) -> list[AxeClassement]:
    requete = db.query(AxeClassement)
    if projet_id is not None:
        requete = requete.filter(AxeClassement.projet_id == projet_id)
    if type is not None:
        requete = requete.filter(AxeClassement.type == type)
    return requete.order_by(AxeClassement.type, AxeClassement.valeur).all()


@router.get("/{axe_id}", response_model=AxeClassementLecture)
def lire_axe(axe_id: uuid.UUID, db: Session = Depends(get_db)) -> AxeClassement:
    axe = db.get(AxeClassement, axe_id)
    if axe is None:
        raise HTTPException(404, "Axe de classement introuvable.")
    return axe


@router.patch("/{axe_id}", response_model=AxeClassementLecture)
def modifier_axe(axe_id: uuid.UUID, payload: AxeClassementMaJ, db: Session = Depends(get_db)) -> AxeClassement:
    axe = db.get(AxeClassement, axe_id)
    if axe is None:
        raise HTTPException(404, "Axe de classement introuvable.")

    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(axe, champ, valeur)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Un axe de ce type et cette valeur existe déjà pour ce Projet.") from exc
    db.refresh(axe)
    return axe


@router.delete("/{axe_id}", status_code=204)
def supprimer_axe(axe_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    axe = db.get(AxeClassement, axe_id)
    if axe is None:
        raise HTTPException(404, "Axe de classement introuvable.")

    db.delete(axe)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            409, "Cet axe est encore rattaché à des Entrées ou des liens d'accès — impossible de le supprimer."
        ) from exc
