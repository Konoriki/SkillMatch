# Manuel

## Déploiement

### En local (sans Docker)

```
python -m venv venv
venv\Scripts\activate          # sous Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Puis ouvrir http://localhost:8000. La base SQLite (`skillmatch.db`) se crée
toute seule au premier lancement, à la racine du projet.

### Avec Docker

```
docker build -t skillmatch .
docker run -p 8000:8000 skillmatch
```

Le `Dockerfile` a été écrit et relu avec attention, mais je n'ai pas Docker
installé sur ma machine de dev pour le tester réellement. À vérifier avant
la soutenance.

## Utilisation

1. Aller sur la page d'accueil.
2. Dans "Ajouter un CV", choisir un fichier PDF et cliquer sur "Envoyer".
   Le candidat apparaît dans le tableau en dessous, avec les compétences
   détectées automatiquement.
3. Pour chercher un candidat par compétence, taper un mot dans "Rechercher
   un candidat par compétence" (ex : "Python"). La recherche n'est pas
   sensible à la casse.

### Limites à connaître

- Taille max d'un CV : 5 Mo.
- Seules les compétences présentes dans `app/skills.py` sont reconnues (voir
  "Mise à jour" ci-dessous pour en ajouter).
- Un CV scanné en image (pas de vrai texte dans le PDF) ne donnera aucune
  compétence détectée : `pdfplumber` extrait du texte, il ne fait pas d'OCR.

## Mise à jour

### Ajouter une compétence reconnue

Éditer `app/skills.py` et ajouter le mot dans la bonne catégorie du
dictionnaire. Pas besoin de toucher au reste du code.

### Ajouter une dépendance

L'ajouter dans `requirements.txt` avec une version fixée (ex :
`nom-du-package==1.2.3`), puis `pip install -r requirements.txt`.

### Modifier le schéma de la base

Il n'y a pas d'outil de migration (type Alembic) sur ce projet. Si on change
un modèle dans `app/database.py`, il faut supprimer le fichier
`skillmatch.db` pour repartir sur une base vide (donc perte des données de
test). C'est une limite acceptée pour un projet de cette taille.

### Avant de pousser du code

```
ruff check .
pytest --cov=app --cov-report=term-missing
```

La CI GitHub Actions relance les deux automatiquement à chaque push.
