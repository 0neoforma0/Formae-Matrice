# Infrastructure de production — statut

Backlog Lot 1 : sauvegardes automatiques quotidiennes, PITR 30 jours,
réplication multi-AZ (ADR-0010).

**Décision du 11/08/2026** : ces éléments ne sont provisionnés sur
Scaleway qu'au Lot 6 (test terrain réel), pas avant — développement en
local (Docker Compose) jusqu'au Lot 5. Cette note documente ce qui reste
à faire, pour qu'aucune décision ne se reperde entre deux sessions.

## À provisionner au Lot 6

- Instance PostgreSQL managée Scaleway (Database as a Service), schéma
  par agence (ADR-0009), même modèle que le développement local.
- Sauvegardes automatiques quotidiennes — activées par défaut sur les
  instances managées Scaleway, à vérifier explicitement au provisioning.
- PITR (Point-In-Time Recovery) 30 jours — paramètre de rétention à fixer
  à la création de l'instance, pas modifiable après coup sans migration.
- Réplication multi-AZ — nécessite un plan Scaleway Business ou supérieur ;
  à confirmer contre le budget réel avant le Lot 6 (point non chiffré à
  ce jour).
- Stockage objet (Scaleway Object Storage) pour `piece_justificative.fichier_url`
  — actuellement un simple champ texte en local, sans backend réel branché.

## Non fait volontairement

Aucun script Terraform/Pulumi n'est écrit à ce stade — l'objet de ce
document est de fixer la liste, pas l'outillage d'infrastructure, qui
sera choisi au moment du Lot 6 en fonction de ce qui existe alors chez
Scaleway.
