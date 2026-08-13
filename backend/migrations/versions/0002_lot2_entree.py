"""Lot 2 — Cœur fonctionnel : entree, version, piece_justificative, proposition_entree

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-11

Immutabilité de `version` (aucun UPDATE/DELETE applicatif) : le REVOKE
sur le rôle applicatif est posé par scripts/provision_tenant.py, pas ici
— cette migration ne connaît pas encore le nom du rôle par agence.

Pièce justificative optionnelle (décision 11/08/2026) : `version_piece`
reste une simple table de jonction, aucune contrainte NOT NULL ne force
une pièce à l'Entrée.

Proposition d'Entrée (Contrat de compatibilité intersystèmes F-05,
10/08/2026) : objet candidat que seule cette migration matérialise
en Entrée réelle — voir app/api/v1/propositions.py.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "entree",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("projet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projet.id"), nullable=False),
        sa.Column("code_lecture", sa.String, nullable=False),
        sa.Column("nature", sa.String, nullable=False),
        sa.Column("statut", sa.String, nullable=False, server_default="Active"),
        sa.Column("version_active_id", postgresql.UUID(as_uuid=True), nullable=True),  # FK ajoutée plus bas
        sa.Column("phase_alerte_id", sa.SmallInteger, sa.ForeignKey("phase.id"), nullable=True),
        sa.Column("sensible", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("date_creation", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("nature IN ('Decision', 'Constat', 'Contrainte', 'Jalon')", name="ck_entree_nature"),
        sa.CheckConstraint("statut IN ('Active', 'Perimee')", name="ck_entree_statut"),
        sa.UniqueConstraint("projet_id", "code_lecture", name="uq_entree_projet_code_lecture"),
    )

    op.create_table(
        "version",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entree_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("entree.id"), nullable=False),
        sa.Column("valeur", sa.String, nullable=False),
        sa.Column("phase_id", sa.SmallInteger, sa.ForeignKey("phase.id"), nullable=False),
        sa.Column("date_effective", sa.Date, nullable=False),
        sa.Column("date_effective_precision", sa.String, nullable=False, server_default="exacte"),
        sa.Column("declare_par_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("titulaire.id"), nullable=False),
        sa.Column("statut", sa.String, nullable=False, server_default="Active"),
        sa.Column("cloture", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("attributs", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("date_creation", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("statut IN ('Active', 'Perimee')", name="ck_version_statut"),
        sa.CheckConstraint(
            "date_effective_precision IN ('exacte', 'approximative')", name="ck_version_date_precision"
        ),
    )

    # FK circulaire entree.version_active_id -> version.id, posée après coup.
    op.create_foreign_key(
        "fk_entree_version_active", "entree", "version", ["version_active_id"], ["id"]
    )

    # Immutabilité — DEC-M027 : aucun UPDATE/DELETE applicatif sur version.
    # (le REVOKE effectif sur le rôle par agence est posé au provisioning tenant)

    op.create_table(
        "piece_justificative",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("date_diffusion", sa.Date, nullable=False),
        sa.Column("origine", sa.String, nullable=False),
        sa.Column("fichier_url", sa.String, nullable=False),
        sa.Column("reference_externe", sa.String, nullable=True),
        sa.Column("date_creation", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("origine IN ('import_pilotis', 'depot_direct')", name="ck_piece_origine"),
    )

    op.create_table(
        "proposition_entree",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("projet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projet.id"), nullable=False),
        sa.Column("source", sa.String, nullable=False),
        sa.Column("nature_proposee", sa.String, nullable=False),
        sa.Column("contenu_propose", sa.Text, nullable=False),
        sa.Column("attributs_proposes", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("statut", sa.String, nullable=False, server_default="En_attente"),
        sa.Column("entree_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("entree.id"), nullable=True),
        sa.Column("materialisee_par_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("titulaire.id"), nullable=True),
        sa.Column("date_proposition", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("date_traitement", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("nature_proposee IN ('Decision', 'Constat', 'Contrainte', 'Jalon')", name="ck_proposition_nature"),
        sa.CheckConstraint("source IN ('Prisme', 'Pilotis', 'Interne')", name="ck_proposition_source"),
        sa.CheckConstraint("statut IN ('En_attente', 'Materialisee', 'Rejetee')", name="ck_proposition_statut"),
    )

    op.create_table(
        "version_piece",
        sa.Column("version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("version.id"), primary_key=True),
        sa.Column("piece_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("piece_justificative.id"), primary_key=True),
    )

    op.create_table(
        "entree_axe",
        sa.Column("entree_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("entree.id"), primary_key=True),
        sa.Column("axe_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("axe_classement.id"), primary_key=True),
    )

    op.create_table(
        "entree_intervenant",
        sa.Column("entree_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("entree.id"), primary_key=True),
        sa.Column("intervenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("intervenant.id"), primary_key=True),
    )

    op.create_index("idx_entree_projet", "entree", ["projet_id"])
    op.create_index("idx_version_entree", "version", ["entree_id"])
    op.execute(
        "CREATE INDEX idx_version_fulltext ON version USING GIN (to_tsvector('french', valeur))"
    )


def downgrade() -> None:
    op.drop_index("idx_version_fulltext", table_name="version")
    op.drop_index("idx_version_entree", table_name="version")
    op.drop_index("idx_entree_projet", table_name="entree")
    op.drop_table("entree_intervenant")
    op.drop_table("entree_axe")
    op.drop_table("version_piece")
    op.drop_table("proposition_entree")
    op.drop_table("piece_justificative")
    op.drop_constraint("fk_entree_version_active", "entree", type_="foreignkey")
    op.drop_table("version")
    op.drop_table("entree")
