# Processus de mise à jour des dépendances

## Fréquence

- **Automatique** : Dependabot ouvre une pull request dès qu'une nouvelle
  version d'une dépendance Python (`requirements.txt`) ou d'une action
  GitHub (`.github/workflows/`) est disponible, vérifiée chaque **semaine**
  (`.github/dependabot.yml`).
- **Manuel** : à chaque alerte de sécurité (Dependabot alerts, ou échec du
  job `pip-audit` en CI), traitement prioritaire sans attendre le cycle
  hebdomadaire.

## Périmètre

- Dépendances applicatives directes listées dans `requirements.txt`.
- Actions GitHub utilisées dans `.github/workflows/ci.yml`.
- Les dépendances transitives (ex. `starlette` via `fastapi`,
  `pdfminer-six` via `pdfplumber`) sont mises à jour indirectement, en
  faisant monter de version le paquet direct qui les embarque.

## Type de mise à jour

| Déclencheur | Type | Action |
|---|---|---|
| Nouvelle version mineure/patch, CI verte | Automatique | La PR Dependabot est mergée après revue rapide (CI passante = validation) |
| Nouvelle version majeure | Manuel | Revue du changelog de la dépendance avant merge (risque de rupture) |
| Vulnérabilité détectée par `pip-audit` en CI | Manuel, prioritaire | Mise à jour immédiate du paquet concerné, tests relancés, correctif documenté dans `CHANGELOG.md` |

## Outils

- **Dependabot** (`.github/dependabot.yml`) : détection et proposition de
  mise à jour automatique via pull request.
- **pip-audit** (étape de `.github/workflows/ci.yml`) : scan des
  vulnérabilités connues (base [PyPA Advisory Database](https://github.com/pypa/advisory-database))
  sur `requirements.txt` à chaque exécution de la CI. Un scan en échec fait
  échouer le job `lint-and-test`.

## Exemple réel (v1.1.0, 2026-08-18)

Premier passage de `pip-audit` sur le projet : **21 vulnérabilités connues
détectées sur 5 paquets** (`python-multipart`, `jinja2`, `pytest`,
`pdfminer-six` via `pdfplumber`, `starlette` via `fastapi`). Traitement :

1. Mise à jour des paquets directement concernés vers leur dernière version
   patchée (`python-multipart`, `jinja2`, `pytest`), et des paquets parents
   pour corriger les dépendances transitives vulnérables (`fastapi` →
   `starlette` patché, `pdfplumber` → `pdfminer-six` patché).
2. Suite de tests complète relancée : 24/24 tests passent, aucune
   régression.
3. `pip-audit` relancé : 0 vulnérabilité restante.
4. Changement documenté dans `CHANGELOG.md` (version 1.1.0).

Voir `requirements.txt` (diff du commit de mise à jour) pour le détail des
versions.
