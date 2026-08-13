"""
Provisioning multi-tenant — ADR-0009.

Crée un schéma PostgreSQL dédié + un rôle applicatif par agence, avec
droits GRANT/REVOKE explicites. Immutabilité de `version` et
`piece_justificative` (DEC-M027) appliquée ici par REVOKE, pas au
niveau applicatif — c'est la base qui interdit, pas seulement le code.

MVP : une seule agence (le titulaire). Ce script est appelé manuellement,
une fois, pour cette agence — pas encore automatisé en CLI tant qu'il
n'y a pas de second client réel (décision d'ouverture du Lot 1, 11/08/2026).

Usage :
    python scripts/provision_tenant.py --agence formae-pilote
"""

import argparse
import sys

from sqlalchemy import text

from app.core.database import engine

TABLES_IMMUTABLES = ("version", "piece_justificative", "consultation")


def provisionner(nom_agence: str) -> None:
    schema = f"agence_{nom_agence}"
    role = f"role_{nom_agence}"

    with engine.begin() as conn:
        print(f"→ Création du schéma « {schema} »")
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

        print(f"→ Création du rôle applicatif « {role} »")
        conn.execute(
            text(
                f"DO $$ BEGIN "
                f"IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{role}') THEN "
                f"CREATE ROLE {role} LOGIN; "
                f"END IF; END $$;"
            )
        )

        print(f"→ Attribution des droits sur « {schema} » à « {role} »")
        conn.execute(text(f'GRANT USAGE ON SCHEMA "{schema}" TO {role}'))
        conn.execute(text(f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA "{schema}" TO {role}'))
        conn.execute(text(f'GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "{schema}" TO {role}'))

        print("→ Application de l'immutabilité (REVOKE UPDATE/DELETE) sur les tables append-only")
        for table in TABLES_IMMUTABLES:
            conn.execute(text(f'REVOKE UPDATE, DELETE ON "{schema}"."{table}" FROM {role}'))
            print(f"  · {table} — UPDATE/DELETE révoqués pour {role}")

    print(f"✓ Agence « {nom_agence} » provisionnée (schéma {schema}, rôle {role}).")
    print("  Prochaine étape : appliquer les migrations sur ce schéma (alembic -x schema=" + schema + " upgrade head).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provisionne un nouveau schéma d'agence (multi-tenant, ADR-0009).")
    parser.add_argument("--agence", required=True, help="Identifiant court de l'agence (ex. formae-pilote)")
    args = parser.parse_args()

    if not args.agence.replace("-", "").replace("_", "").isalnum():
        print("Erreur : l'identifiant d'agence doit être alphanumérique (tirets/underscores autorisés).")
        sys.exit(1)

    provisionner(args.agence.replace("-", "_"))
