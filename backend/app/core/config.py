"""
Configuration centrale — Matrice.

Un seul titulaire (compte agence) au MVP. L'identité nominative
individuelle est différée en V2 (décision Session A, 10/08/2026) ;
ce fichier ne doit jamais figer en dur une hypothèse contraire.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+psycopg://matrice:matrice_dev_local@localhost:5432/matrice"

    # Lot 4 — expiration des liens d'accès externes après inactivité.
    # Décision 11/08/2026 : 90 jours, réinitialisé à chaque consultation.
    lien_acces_expiration_jours: int = 90

    # Lot 5 — import de documents validés : PDF uniquement au MVP (décision 11/08/2026).
    formats_import_autorises: tuple[str, ...] = (".pdf",)


settings = Settings()
