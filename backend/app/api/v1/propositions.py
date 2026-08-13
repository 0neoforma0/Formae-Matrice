import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entree import Entree
from app.models.projet import Projet
from app.models.proposition_entree import PropositionEntree
from app.models.titulaire import Titulaire
from app.models.version import Version
from app.schemas.proposition_entree import (
    PropositionEntreeCreation,
    PropositionEntreeLecture,
    PropositionMaterialisation,
)

router = APIRouter(prefix="/propositions", tags=["propositions"])


@router.post("", response_model=PropositionEntreeLecture, status_code=201)
def creer_proposition(payload: PropositionEntreeCreation, db: Session = Depends(get_db)) -> PropositionEntree:
    """
    Prisme et Pilotis n'ont pas d'Entrées : ils déposent une Proposition
    d'Entrée. Elle ne devient une Entrée qu'après matérialisation par
    Matrice (Article 5 de la Constitution — Matrice seule décide de ce
    qui entre chez elle).
    """
    projet = db.get(Projet, payload.projet_id)
    if projet is None:
        raise HTTPException(404, "Projet introuvable.")

    proposition = PropositionEntree(
        projet_id=payload.projet_id,
        source=payload.source,
        nature_proposee=payload.nature_proposee,
        contenu_propose=payload.contenu_propose,
        attributs_proposes=payload.attributs_proposes,
    )
    db.add(proposition)
    db.commit()
    db.refresh(proposition)
    return proposition


@router.post("/{proposition_id}/materialiser", response_model=PropositionEntreeLecture)
def materialiser_proposition(
    proposition_id: uuid.UUID,
    payload: PropositionMaterialisation,
    db: Session = Depends(get_db),
) -> PropositionEntree:
    """
    Seul le titulaire matérialise ou rejette une proposition (modèle
    d'accès à deux niveaux). TODO Lot 4 : brancher l'authentification
    réelle du titulaire une fois les liens d'accès en place — cet
    endpoint est aujourd'hui ouvert car aucun autre rôle ne peut encore
    s'authentifier.
    """
    proposition = db.get(PropositionEntree, proposition_id)
    if proposition is None:
        raise HTTPException(404, "Proposition introuvable.")
    if proposition.statut != "En_attente":
        raise HTTPException(409, f"Proposition déjà traitée (statut : {proposition.statut}).")

    if not payload.accepter:
        proposition.statut = "Rejetee"
        proposition.date_traitement = datetime.utcnow()
        db.commit()
        db.refresh(proposition)
        return proposition

    if payload.phase_id is None or payload.date_effective is None:
        raise HTTPException(422, "phase_id et date_effective requis pour matérialiser.")

    projet = db.get(Projet, proposition.projet_id)
    projet.dernier_numero_entree += 1
    code_lecture = f"{projet.nom.upper().replace(' ', '')}-{projet.dernier_numero_entree:04d}"

    entree = Entree(
        projet_id=proposition.projet_id,
        code_lecture=code_lecture,
        nature=proposition.nature_proposee,
    )
    db.add(entree)
    db.flush()

    titulaire = db.query(Titulaire).first()
    if titulaire is None:
        raise HTTPException(412, "Aucun titulaire enregistré — impossible de matérialiser.")

    version = Version(
        entree_id=entree.id,
        valeur=proposition.contenu_propose,
        phase_id=payload.phase_id,
        date_effective=payload.date_effective,
        attributs=proposition.attributs_proposes,
        declare_par_id=titulaire.id,
    )
    db.add(version)
    db.flush()

    entree.version_active_id = version.id

    proposition.statut = "Materialisee"
    proposition.entree_id = entree.id
    proposition.materialisee_par_id = titulaire.id
    proposition.date_traitement = datetime.utcnow()

    db.commit()
    db.refresh(proposition)
    return proposition
