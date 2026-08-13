import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validation import valider_attributs
from app.models.axe_classement import AxeClassement
from app.models.entree import Entree
from app.models.jonctions import entree_axe, entree_intervenant, version_piece
from app.models.phase import Phase
from app.models.piece_justificative import PieceJustificative
from app.models.projet import Projet
from app.models.titulaire import Titulaire
from app.models.version import Version
from app.schemas.entree import EntreeCreation, EntreeLecture, VersionCreation, VersionLecture

router = APIRouter(prefix="/entrees", tags=["entrees"])


def _titulaire_unique(db: Session) -> Titulaire:
    """
    Au MVP il n'y a qu'un seul titulaire (modèle d'accès à deux niveaux —
    identité nominative individuelle différée en V2, décision Session A
    du 10/08/2026). Tant qu'il n'y a pas d'authentification (Lot 4), c'est
    ce titulaire unique qui est réputé auteur de toute Version créée.

    TODO Lot 4 : remplacer par le titulaire authentifié une fois les
    liens d'accès et la session en place.
    """
    titulaire = db.query(Titulaire).first()
    if titulaire is None:
        raise HTTPException(
            412,
            "Aucun titulaire enregistré — créer le compte agence avant toute Entrée.",
        )
    return titulaire


def _code_lecture_suivant(db: Session, projet: Projet) -> str:
    """Attribue le prochain code de lecture — jamais réattribué (append-only)."""
    projet.dernier_numero_entree += 1
    db.flush()
    return f"{projet.nom.upper().replace(' ', '')}-{projet.dernier_numero_entree:04d}"


def _appliquer_bascule_jalon(db: Session, projet: Projet, nature: str, attributs: dict) -> None:
    """Mécanisme Jalon → bascule de Projet.phase_courante_id (Backlog Lot 2)."""
    if nature != "Jalon":
        return
    phase_id = attributs["phase_declenchee"]  # présence garantie par valider_attributs
    phase = db.get(Phase, phase_id)
    if phase is None:
        raise HTTPException(422, f"Phase inconnue : {phase_id}")
    projet.phase_courante_id = phase.id


@router.post("", response_model=EntreeLecture, status_code=201)
def creer_entree(payload: EntreeCreation, db: Session = Depends(get_db)) -> Entree:
    """
    Crée une Entrée avec sa première Version.

    Pièce justificative optionnelle (décision 11/08/2026) : `piece_ids`
    peut être vide, la création n'est jamais bloquée par son absence.

    Sensibilité effective : `sensible` (manuel) OU tout axe rattaché
    marqué `sensible` (héritage) — décision 11/08/2026.

    Une Entrée de nature Jalon fait immédiatement basculer la phase
    courante du Projet (Backlog Lot 2).
    """
    projet = db.get(Projet, payload.projet_id)
    if projet is None:
        raise HTTPException(404, "Projet introuvable.")

    if payload.nature not in ("Decision", "Constat", "Contrainte", "Jalon"):
        raise HTTPException(422, f"Nature inconnue : {payload.nature}")

    valider_attributs(payload.nature, payload.version_initiale.attributs)

    entree = Entree(
        projet_id=projet.id,
        code_lecture=_code_lecture_suivant(db, projet),
        nature=payload.nature,
        sensible=payload.sensible,
        phase_alerte_id=payload.phase_alerte_id,
        statut="Perimee" if payload.version_initiale.cloture else "Active",
    )
    db.add(entree)
    db.flush()  # obtenir entree.id avant de créer la Version

    titulaire = _titulaire_unique(db)
    version = Version(
        entree_id=entree.id,
        valeur=payload.version_initiale.valeur,
        phase_id=payload.version_initiale.phase_id,
        date_effective=payload.version_initiale.date_effective,
        date_effective_precision=payload.version_initiale.date_effective_precision,
        attributs=payload.version_initiale.attributs,
        declare_par_id=titulaire.id,
        cloture=payload.version_initiale.cloture,
    )
    db.add(version)
    db.flush()

    entree.version_active_id = version.id

    for piece_id in payload.version_initiale.piece_ids:
        piece = db.get(PieceJustificative, piece_id)
        if piece is None:
            raise HTTPException(404, f"Pièce justificative introuvable : {piece_id}")
        db.execute(version_piece.insert().values(version_id=version.id, piece_id=piece.id))

    for axe_id in payload.axe_ids:
        db.execute(entree_axe.insert().values(entree_id=entree.id, axe_id=axe_id))

    for intervenant_id in payload.intervenant_ids:
        db.execute(entree_intervenant.insert().values(entree_id=entree.id, intervenant_id=intervenant_id))

    _appliquer_bascule_jalon(db, projet, payload.nature, payload.version_initiale.attributs)

    db.commit()
    db.refresh(entree)
    return entree


@router.post("/{entree_id}/versions", response_model=EntreeLecture, status_code=201)
def ajouter_version(entree_id: uuid.UUID, payload: VersionCreation, db: Session = Depends(get_db)) -> Entree:
    """
    Ajoute une nouvelle Version à une Entrée existante (append-only —
    aucune Version n'est jamais modifiée ni supprimée, y compris celle-ci).

    Clôture (Backlog Lot 2) : si `cloture=true`, l'Entrée passe au statut
    Perimee. Une Entrée déjà Perimee ne peut plus recevoir de Version.

    Jalon : si l'Entrée est de nature Jalon, la phase courante du Projet
    bascule sur `attributs.phase_declenchee` à chaque nouvelle Version.
    """
    entree = db.get(Entree, entree_id)
    if entree is None:
        raise HTTPException(404, "Entrée introuvable.")
    if entree.statut == "Perimee":
        raise HTTPException(409, "Cette Entrée est Perimee — aucune nouvelle Version ne peut lui être ajoutée.")

    valider_attributs(entree.nature, payload.attributs)

    projet = db.get(Projet, entree.projet_id)
    titulaire = _titulaire_unique(db)

    version = Version(
        entree_id=entree.id,
        valeur=payload.valeur,
        phase_id=payload.phase_id,
        date_effective=payload.date_effective,
        date_effective_precision=payload.date_effective_precision,
        attributs=payload.attributs,
        declare_par_id=titulaire.id,
        cloture=payload.cloture,
    )
    db.add(version)
    db.flush()

    for piece_id in payload.piece_ids:
        piece = db.get(PieceJustificative, piece_id)
        if piece is None:
            raise HTTPException(404, f"Pièce justificative introuvable : {piece_id}")
        db.execute(version_piece.insert().values(version_id=version.id, piece_id=piece.id))

    entree.version_active_id = version.id
    if payload.cloture:
        entree.statut = "Perimee"

    _appliquer_bascule_jalon(db, projet, entree.nature, payload.attributs)

    db.commit()
    db.refresh(entree)
    return entree


@router.get("/{entree_id}/versions", response_model=list[VersionLecture])
def lister_versions(entree_id: uuid.UUID, db: Session = Depends(get_db)) -> list[Version]:
    """Historique complet, append-only — jamais tronqué ni réécrit."""
    entree = db.get(Entree, entree_id)
    if entree is None:
        raise HTTPException(404, "Entrée introuvable.")
    return db.query(Version).filter(Version.entree_id == entree_id).order_by(Version.date_creation).all()


@router.get("/{entree_id}", response_model=EntreeLecture)
def lire_entree(entree_id: uuid.UUID, db: Session = Depends(get_db)) -> Entree:
    entree = db.get(Entree, entree_id)
    if entree is None:
        raise HTTPException(404, "Entrée introuvable.")
    return entree


@router.get("/{entree_id}/sensible-effective")
def sensible_effective(entree_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    """
    Calcule la sensibilité effective : `sensible` (manuel) OU un axe
    rattaché marqué `sensible` (hérité). Jamais stocké en double —
    toujours recalculé pour éviter toute désynchronisation.
    """
    entree = db.get(Entree, entree_id)
    if entree is None:
        raise HTTPException(404, "Entrée introuvable.")

    axe_ids = [row.axe_id for row in db.execute(entree_axe.select().where(entree_axe.c.entree_id == entree_id))]
    axe_sensible = False
    if axe_ids:
        axe_sensible = (
            db.query(AxeClassement).filter(AxeClassement.id.in_(axe_ids), AxeClassement.sensible.is_(True)).first()
            is not None
        )

    return {
        "entree_id": str(entree_id),
        "sensible_manuel": entree.sensible,
        "sensible_herite": axe_sensible,
        "sensible_effective": entree.sensible or axe_sensible,
    }
