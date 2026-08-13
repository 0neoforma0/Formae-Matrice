import uuid

import pytest

from app.core.database import SessionLocal
from app.models.projet import Projet
from app.models.titulaire import Titulaire


@pytest.fixture
def titulaire():
    """Un Titulaire réel en base — nécessaire pour tout ce qui exige le titulaire unique du MVP."""
    db = SessionLocal()
    t = Titulaire(nom_agence="Formae Test", email=f"test-{uuid.uuid4()}@formae.test")
    db.add(t)
    db.commit()
    db.refresh(t)
    db.close()
    return t


@pytest.fixture
def projet(titulaire):
    """Un Projet réel en base, rattaché au Titulaire de test."""
    db = SessionLocal()
    p = Projet(titulaire_id=titulaire.id, nom=f"Projet {uuid.uuid4().hex[:8]}")
    db.add(p)
    db.commit()
    db.refresh(p)
    db.close()
    return p
