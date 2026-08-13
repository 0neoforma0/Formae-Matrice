"""Tables de jonction — pas d'attributs propres, clés primaires composées."""

import uuid

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

version_piece = Table(
    "version_piece",
    Base.metadata,
    Column("version_id", UUID(as_uuid=True), ForeignKey("version.id"), primary_key=True),
    Column("piece_id", UUID(as_uuid=True), ForeignKey("piece_justificative.id"), primary_key=True),
)

entree_axe = Table(
    "entree_axe",
    Base.metadata,
    Column("entree_id", UUID(as_uuid=True), ForeignKey("entree.id"), primary_key=True),
    Column("axe_id", UUID(as_uuid=True), ForeignKey("axe_classement.id"), primary_key=True),
)

entree_intervenant = Table(
    "entree_intervenant",
    Base.metadata,
    Column("entree_id", UUID(as_uuid=True), ForeignKey("entree.id"), primary_key=True),
    Column("intervenant_id", UUID(as_uuid=True), ForeignKey("intervenant.id"), primary_key=True),
)

lien_axe_scope = Table(
    "lien_axe_scope",
    Base.metadata,
    Column("lien_id", UUID(as_uuid=True), ForeignKey("lien_acces.id"), primary_key=True),
    Column("axe_id", UUID(as_uuid=True), ForeignKey("axe_classement.id"), primary_key=True),
)
