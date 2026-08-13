"""
Tests Lot 3 — Classification et répertoire :
  - CRUD Intervenant (répertoire d'agence, réutilisable entre projets)
  - CRUD Axe de classement (Lot / Ouvrage / Localisation)
  - rattachement/détachement a posteriori des axes et intervenants sur une Entrée

Nécessite une base PostgreSQL locale (voir docker-compose.yml) et les
migrations appliquées : `alembic upgrade head` avant `pytest`. Les tests
marqués `integration` utilisent les fixtures `titulaire`/`projet`
(conftest.py) pour créer de vraies données et exercer le mécanisme de
bout en bout, pas seulement le contrat de l'API.
"""

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_creer_axe_type_inconnu_rejete() -> None:
    """Un type d'axe hors de ('Lot', 'Ouvrage', 'Localisation') est rejeté — pas besoin de DB pour ce contrat."""
    payload = {"projet_id": str(uuid.uuid4()), "type": "Phase", "valeur": "Faisabilite"}
    response = client.post("/api/v1/axes", json=payload)
    assert response.status_code in (422, 404)


@pytest.mark.integration
def test_rattacher_axe_entree_inconnue() -> None:
    """Rattacher un axe à une Entrée inexistante échoue — documente le contrat (voir test_entrees.py)."""
    response = client.post(f"/api/v1/entrees/{uuid.uuid4()}/axes/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.integration
def test_creer_intervenant(titulaire) -> None:
    """Un Intervenant est un répertoire d'agence, jamais rattaché à un Projet."""
    payload = {"nom": "Jean Dupont", "role": "Architecte", "entreprise": "Atelier Dupont"}
    response = client.post("/api/v1/intervenants", json=payload)
    assert response.status_code == 201
    corps = response.json()
    assert "projet_id" not in corps
    assert corps["nom"] == "Jean Dupont"
    assert corps["titulaire_id"] == str(titulaire.id)


@pytest.mark.integration
def test_crud_axe_classement(projet) -> None:
    """Cycle complet : créer, lire, modifier, supprimer un axe non rattaché."""
    creation = client.post(
        "/api/v1/axes", json={"projet_id": str(projet.id), "type": "Lot", "valeur": "Lot 3 — Gros œuvre"}
    )
    assert creation.status_code == 201
    axe_id = creation.json()["id"]
    assert creation.json()["sensible"] is False

    lecture = client.get(f"/api/v1/axes/{axe_id}")
    assert lecture.status_code == 200
    assert lecture.json()["valeur"] == "Lot 3 — Gros œuvre"

    maj = client.patch(f"/api/v1/axes/{axe_id}", json={"sensible": True})
    assert maj.status_code == 200
    assert maj.json()["sensible"] is True

    suppression = client.delete(f"/api/v1/axes/{axe_id}")
    assert suppression.status_code == 204
    assert client.get(f"/api/v1/axes/{axe_id}").status_code == 404


def _creer_entree(projet_id: uuid.UUID) -> str:
    payload = {
        "projet_id": str(projet_id),
        "nature": "Decision",
        "version_initiale": {
            "valeur": "Choix de test",
            "phase_id": 1,
            "date_effective": str(date.today()),
        },
    }
    response = client.post("/api/v1/entrees", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.integration
def test_rattacher_axe_a_une_entree_et_heritage_sensibilite(projet, titulaire) -> None:
    """
    Bout en bout : un axe créé après l'Entrée peut lui être rattaché, et un
    axe sensible rattaché rend l'Entrée sensible par héritage (Lot 2) — même
    quand le rattachement se fait a posteriori (Lot 3), pas seulement à la
    création.
    """
    entree_id = _creer_entree(projet.id)

    axe = client.post(
        "/api/v1/axes", json={"projet_id": str(projet.id), "type": "Ouvrage", "valeur": "Fondations", "sensible": True}
    )
    assert axe.status_code == 201
    axe_id = axe.json()["id"]

    avant = client.get(f"/api/v1/entrees/{entree_id}/sensible-effective").json()
    assert avant["sensible_herite"] is False

    rattachement = client.post(f"/api/v1/entrees/{entree_id}/axes/{axe_id}")
    assert rattachement.status_code == 201
    assert axe_id in [a["id"] for a in rattachement.json()]

    liste = client.get(f"/api/v1/entrees/{entree_id}/axes")
    assert liste.status_code == 200
    assert [a["id"] for a in liste.json()] == [axe_id]

    apres = client.get(f"/api/v1/entrees/{entree_id}/sensible-effective").json()
    assert apres["sensible_herite"] is True
    assert apres["sensible_effective"] is True

    detachement = client.delete(f"/api/v1/entrees/{entree_id}/axes/{axe_id}")
    assert detachement.status_code == 204

    apres_detachement = client.get(f"/api/v1/entrees/{entree_id}/sensible-effective").json()
    assert apres_detachement["sensible_herite"] is False


@pytest.mark.integration
def test_rattacher_intervenant_a_une_entree(projet) -> None:
    """Bout en bout : rattacher/lister/détacher un Intervenant sur une Entrée existante."""
    entree_id = _creer_entree(projet.id)

    intervenant = client.post("/api/v1/intervenants", json={"nom": "Marie Curie", "role": "BET Structure"})
    assert intervenant.status_code == 201
    intervenant_id = intervenant.json()["id"]

    rattachement = client.post(f"/api/v1/entrees/{entree_id}/intervenants/{intervenant_id}")
    assert rattachement.status_code == 201
    assert intervenant_id in [i["id"] for i in rattachement.json()]

    liste = client.get(f"/api/v1/entrees/{entree_id}/intervenants")
    assert [i["id"] for i in liste.json()] == [intervenant_id]

    detachement = client.delete(f"/api/v1/entrees/{entree_id}/intervenants/{intervenant_id}")
    assert detachement.status_code == 204
    assert client.get(f"/api/v1/entrees/{entree_id}/intervenants").json() == []


@pytest.mark.integration
def test_suppression_axe_rattache_bloquee(projet) -> None:
    """Un axe encore rattaché à une Entrée ne peut pas être supprimé (409), pas d'erreur 500 brute."""
    entree_id = _creer_entree(projet.id)
    axe = client.post("/api/v1/axes", json={"projet_id": str(projet.id), "type": "Localisation", "valeur": "Bat A"})
    axe_id = axe.json()["id"]
    client.post(f"/api/v1/entrees/{entree_id}/axes/{axe_id}")

    suppression = client.delete(f"/api/v1/axes/{axe_id}")
    assert suppression.status_code == 409

    client.delete(f"/api/v1/entrees/{entree_id}/axes/{axe_id}")
    assert client.delete(f"/api/v1/axes/{axe_id}").status_code == 204
