# Journal des versions

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
ce projet suit le [versionnage sémantique](https://semver.org/lang/fr/).

## [1.1.1] - 2026-08-18

### Corrigé
- Race condition sur la création d'une compétence lors d'imports concurrents :
  `add_candidat()` vérifiait puis créait une compétence sans que ce soit
  atomique, ce qui provoquait une `IntegrityError` non gérée (500) quand
  deux requêtes introduisaient la même nouvelle compétence en même temps.
  Ajout d'une retentative après échec du commit, couverte par un test de
  non-régression déterministe
  ([#2](https://github.com/Konoriki/SkillMatch/issues/2)).

## [1.1.0] - 2026-08-18

### Ajouté
- Endpoint `GET /health` : statut de l'application + vérification d'accès
  à la base SQLite.
- Journalisation applicative structurée (requêtes, imports de CV, erreurs
  d'upload/extraction).
- Sonde de supervision `monitoring/probe.py` : interroge `/health` en
  continu ou en vérification unique, journalise disponibilité et temps de
  réponse, alerte en cas d'échec.
- Template d'issue GitHub (`.github/ISSUE_TEMPLATE/bug_report.md`) pour la
  consignation d'anomalies.

### Corrigé
- Recherche par compétence : les métacaractères SQL `%` et `_` saisis par
  l'utilisateur n'étaient pas échappés, ce qui produisait des résultats
  faux et dupliqués (ex. `P%` matchait `Python` et `PHP`). Corrigé et
  couvert par des tests de non-régression ([#1](https://github.com/Konoriki/SkillMatch/issues/1)).

### Sécurité
- `pip-audit` intégré à la CI a détecté 21 vulnérabilités connues sur 5
  paquets (`python-multipart`, `jinja2`, `pytest`, `pdfminer-six` via
  `pdfplumber`, `starlette` via `fastapi`). Dépendances mises à jour vers
  leurs versions patchées ; scan relancé sans vulnérabilité restante. Voir
  `docs/mise_a_jour_dependances.md`.

### Connu (anomalie ouverte, non corrigée dans cette version)
- Vérification `Content-Type` trop stricte à l'upload, pouvant rejeter à
  tort un PDF valide envoyé avec un type MIME générique
  ([#3](https://github.com/Konoriki/SkillMatch/issues/3)).

## [1.0.0] - 2026-07-22

### Ajouté
- Version initiale de SkillMatch : upload de CV au format PDF, extraction
  du texte (pdfplumber), détection de compétences par dictionnaire de
  mots-clés, stockage SQLModel/SQLite, recherche de candidats par
  compétence, interface web Jinja2, intégration continue (lint + tests +
  build Docker).
