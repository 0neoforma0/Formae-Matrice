"""
Validation des attributs JSONB par nature — Schéma de Données Définitif,
tableau « Champs attributs (JSONB) par nature ».

| Nature     | Champs                                              | Obligatoire      |
|------------|------------------------------------------------------|------------------|
| Decision   | (aucun)                                               | —                |
| Constat    | source_methode                                        | Non              |
| Contrainte | niveau ('bloquante'|'a_surveiller'), entrees_impactees | niveau : oui     |
| Jalon      | phase_declenchee (id phase)                           | Oui              |

Cette validation est volontairement centralisée ici (pas dans le modèle
SQLAlchemy ni dans un CHECK JSONB PostgreSQL) : les règles par nature
sont amenées à évoluer plus vite que le schéma de table lui-même.
"""

from fastapi import HTTPException

NIVEAUX_CONTRAINTE = ("bloquante", "a_surveiller")


def valider_attributs(nature: str, attributs: dict) -> None:
    if nature == "Decision":
        return  # aucun champ requis

    if nature == "Constat":
        return  # source_methode optionnel, rien à valider

    if nature == "Contrainte":
        niveau = attributs.get("niveau")
        if niveau not in NIVEAUX_CONTRAINTE:
            raise HTTPException(
                422,
                f"Une Entrée de nature Contrainte exige un champ 'niveau' parmi {NIVEAUX_CONTRAINTE} "
                f"(reçu : {niveau!r}).",
            )
        entrees_impactees = attributs.get("entrees_impactees", [])
        if not isinstance(entrees_impactees, list):
            raise HTTPException(422, "'entrees_impactees' doit être une liste d'identifiants d'Entrée.")
        return

    if nature == "Jalon":
        if "phase_declenchee" not in attributs:
            raise HTTPException(
                422,
                "Une Entrée de nature Jalon exige un champ 'phase_declenchee' (identifiant de phase).",
            )
        return

    raise HTTPException(422, f"Nature inconnue : {nature!r}")
