# SkillMatch

Petite application qui prend des CV au format PDF, en extrait les
compétences techniques (Python, Docker, SQL, ...) et permet de chercher des
candidats par compétence. Projet réalisé dans le cadre du BC02 (RNCP39583).

100 % local : aucune donnée n'est envoyée ailleurs, pas de service payant,
pas besoin de GPU.

## Stack

Python 3.12+, FastAPI, pdfplumber (extraction PDF), SQLModel/SQLite
(stockage), Jinja2 (interface web, sans JS).

## Démarrage rapide

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Puis ouvrir http://localhost:8000.

Pour lancer les tests :

```
pytest --cov=app --cov-report=term-missing
```

Détails complets (déploiement avec Docker, utilisation, mise à jour) dans
[`docs/manuel.md`](docs/manuel.md).

## Structure du projet

```
app/
  main.py         routes FastAPI
  extraction.py   lecture du PDF + détection des compétences
  database.py     modèles et requêtes SQLModel
  skills.py       dictionnaire des compétences reconnues
  templates/      page HTML
  static/         feuille de style
tests/            tests pytest
docs/             architecture, cahier de recettes, manuels, bugs
```

Voir [`docs/architecture.md`](docs/architecture.md) pour le détail de
l'architecture et le schéma, [`docs/ci_cd.md`](docs/ci_cd.md) pour
l'intégration/déploiement continu, et [`docs/accessibilite.md`](docs/accessibilite.md)
pour le référentiel d'accessibilité suivi.
