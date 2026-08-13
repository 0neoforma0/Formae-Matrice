"""Lot 1 — Fondations : titulaire, phase, projet, intervenant, axe_classement

Revision ID: 0001
Revises:
Create Date: 2026-08-11

Provisioning multi-tenant (ADR-0009) : cette migration s'applique
schéma par schéma, une fois par agence (voir scripts/provision_tenant.py).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')  # gen_random_uuid()

    op.create_table(
        "titulaire",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("nom_agence", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("date_creation", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "phase",
        sa.Column("id", sa.SmallInteger, primary_key=True),
        sa.Column("code", sa.String, nullable=False, unique=True),
        sa.Column("ordre", sa.SmallInteger, nullable=False),
    )
    op.bulk_insert(
        sa.table(
            "phase",
            sa.column("id", sa.SmallInteger),
            sa.column("code", sa.String),
            sa.column("ordre", sa.SmallInteger),
        ),
        [
            {"id": 1, "code": "Faisabilite", "ordre": 1},
            {"id": 2, "code": "Conception", "ordre": 2},
            {"id": 3, "code": "Consultation", "ordre": 3},
            {"id": 4, "code": "Chantier", "ordre": 4},
            {"id": 5, "code": "Reception", "ordre": 5},
        ],
    )

    op.create_table(
        "projet",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("titulaire_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("titulaire.id"), nullable=False),
        sa.Column("nom", sa.String, nullable=False),
        sa.Column("typologie", sa.String, nullable=True),
        sa.Column("phase_courante_id", sa.SmallInteger, sa.ForeignKey("phase.id"), nullable=True),
        sa.Column("dernier_numero_entree", sa.Integer, nullable=False, server_default="0"),
        sa.Column("en_avant_plan", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("date_creation", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "intervenant",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("titulaire_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("titulaire.id"), nullable=False),
        sa.Column("nom", sa.String, nullable=False),
        sa.Column("role", sa.String, nullable=True),
        sa.Column("entreprise", sa.String, nullable=True),
        sa.Column("contact", sa.String, nullable=True),
        sa.Column("date_creation", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "axe_classement",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("projet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projet.id"), nullable=False),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("valeur", sa.String, nullable=False),
        # Ajouté le 11/08/2026 — sensibilité héritée par les Entrées rattachées.
        sa.Column("sensible", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.CheckConstraint("type IN ('Lot', 'Ouvrage', 'Localisation')", name="ck_axe_classement_type"),
        sa.UniqueConstraint("projet_id", "type", "valeur", name="uq_axe_classement_projet_type_valeur"),
    )


def downgrade() -> None:
    op.drop_table("axe_classement")
    op.drop_table("intervenant")
    op.drop_table("projet")
    op.drop_table("phase")
    op.drop_table("titulaire")
