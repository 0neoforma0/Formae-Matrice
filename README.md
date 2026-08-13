# Matrice — la mémoire vivante du projet

Formae. Mono-repo (backend + frontend), dev local jusqu'au Lot 5.

## Démarrer en local

```
docker compose up
```

L'API est disponible sur http://localhost:8000 (/health, /api/v1/entrees,
/api/v1/propositions). La base PostgreSQL est initialisée vide — appliquer
les migrations avant toute utilisation :

```
docker compose exec backend alembic upgrade head
```

## Provisioning d'une agence (multi-tenant, ADR-0009)

```
docker compose exec backend python scripts/provision_tenant.py --agence formae-pilote
```

## État — 11/08/2026

Lot 1 (Fondations) et Lot 2 (Entrée, Proposition d'Entrée) ont un schéma et
des endpoints fonctionnels, testés de bout en bout :
- création d'une Entrée sans pièce justificative
- sensibilité héritée d'un axe marqué sensible
- cycle Proposition d'Entrée vers matérialisation par le titulaire

Reste à construire : Lot 3 (répertoire Intervenant complet, scoping),
Lot 4 (accès externe, authentification réelle — actuellement l'API suppose
un titulaire unique sans vérification), Lot 5 (QR code, recherche PDF),
Lot 6 (test terrain).

La traçabilité complète des décisions à l'origine de chaque choix technique
de ce dépôt est dans la base Décisions du workspace Notion Formae.
