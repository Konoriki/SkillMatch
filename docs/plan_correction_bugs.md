# Plan de correction des bogues

## Bugs rencontrés et corrigés

### 1. SQLModel incompatible avec Python 3.14

**Symptôme** : dès la définition d'une table (`class Candidat(SQLModel, table=True)`),
pydantic plantait avec `PydanticUserError: Field 'x' requires a type annotation`,
même pour un champ parfaitement bien typé.

**Cause** : la version de SQLModel prévue au départ (0.0.22) est trop ancienne
pour être compatible avec Python 3.14, installé sur la machine de dev. Vérifié
en reproduisant l'erreur sur un modèle minimal de deux lignes.

**Correction** : mise à jour vers SQLModel 0.0.39 (dernière version dispo).
Le problème a disparu.

### 2. Le fichier de base SQLite se créait au mauvais endroit

**Symptôme** : après avoir lancé le serveur via l'outil de preview, le fichier
`skillmatch.db` s'est retrouvé à la racine de l'utilisateur Windows au lieu
du dossier du projet.

**Cause** : `DATABASE_URL = "sqlite:///skillmatch.db"` utilisait un chemin
relatif, qui dépend du répertoire de travail du processus au moment du
lancement (pas forcément le dossier du projet).

**Correction** : chemin absolu calculé depuis l'emplacement de `database.py`
(`Path(__file__).resolve().parent.parent / "skillmatch.db"`).

### 3. Avertissement de dépréciation sur `datetime.utcnow()`

**Symptôme** : warning à chaque test touchant la base.

**Cause** : `datetime.utcnow()` est dépréciée depuis les versions récentes
de Python.

**Correction** : remplacé par `datetime.now(timezone.utc)`.

## Limites connues (pas des bugs, mais à garder en tête)

- Pas d'OCR : un CV scanné en image ne donnera aucune compétence détectée.
- Détection de compétences par mots-clés : une compétence formulée
  différemment de la liste (ex : "Postgres" au lieu de "PostgreSQL") ne sera
  pas reconnue.
- Pas de suppression de candidat depuis l'interface (pas demandé dans le
  brief, mais bon à savoir si un CV est ajouté par erreur).
