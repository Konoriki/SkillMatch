# Supervision de SkillMatch (C4.1.2)

## Périmètre

L'application est un service local mono-instance (FastAPI + SQLite). Le
périmètre de supervision couvre :
- la disponibilité du serveur applicatif,
- l'accès à la base de données SQLite (dépendance unique de l'application).

Il ne couvre pas l'infrastructure hôte (CPU, disque, réseau) : hors périmètre
pour une application locale à ce stade.

## Indicateurs suivis

| Indicateur | Description | Source |
|---|---|---|
| Disponibilité | `GET /health` répond avec un statut HTTP 200 | `app/main.py` (`/health`) |
| Accès base de données | Une requête `SELECT 1` aboutit sans exception | `app/main.py` (`/health`, champ `checks.database`) |
| Temps de réponse | Durée de l'appel à `/health`, en millisecondes | `monitoring/probe.py` |
| Journal des requêtes | Méthode, chemin, code retour, durée de chaque requête HTTP | `app/main.py` (middleware `log_requests`) |
| Journal des imports de CV | ID candidat, fichier, nombre de compétences détectées | `app/main.py` (route `/upload`) |
| Journal des erreurs | Rejets d'upload (type/taille/PDF invalide) et échecs d'extraction | `app/main.py` (niveaux WARNING/ERROR) |

## Sondes

`monitoring/probe.py` interroge `GET /health` à intervalle régulier
(30 secondes par défaut, configurable via `--interval`) et journalise pour
chaque appel : le statut HTTP obtenu et le temps de réponse.

L'URL par défaut utilise `127.0.0.1` plutôt que `localhost` : sur cette
machine, la résolution de `localhost` ajoutait ~2 secondes de latence
artificielle à chaque mesure (tentative IPv6 puis repli IPv4), faussant
l'indicateur de temps de réponse. Constaté lors de la mise en place de la
sonde (cf. temps de réponse passant de ~2060 ms à ~30 ms après correction).

Deux modes d'exécution :
- **Boucle continue** : `python monitoring/probe.py` — utile en supervision
  permanente pendant que le serveur tourne en local.
- **Vérification unique** : `python monitoring/probe.py --once` — pensé pour
  être appelé par un ordonnanceur externe (Tâche planifiée Windows, cron) ;
  le code de sortie (0 = OK, 1 = échec) permet à l'ordonnanceur de déclencher
  une notification.

## Modalité de signalement

- Chaque vérification échouée (statut ≠ 200, timeout, erreur réseau) génère
  une entrée de niveau **CRITICAL** dans `monitoring/probe.log` (créé au
  premier lancement, ignoré par Git) et sur la sortie standard.
- Côté application, les échecs d'accès à la base sont journalisés en
  **ERROR** via le logger `skillmatch` (voir `app/logging_config.py`), avant
  que `/health` ne renvoie 503.
- Pour ce projet local, le canal de signalement retenu est donc le **journal
  applicatif consultable directement** (fichier + console). Une évolution
  possible — documentée dans les recommandations du dossier BC04 — serait de
  brancher une notification active (email, webhook Slack/Discord) sur les
  entrées CRITICAL du fichier de log, ou sur le code de sortie du mode
  `--once` exécuté par un ordonnanceur.

## Lancer la sonde

```bash
# Terminal 1 : l'application
uvicorn app.main:app --reload

# Terminal 2 : la sonde
python monitoring/probe.py
```
