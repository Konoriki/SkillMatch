# Intégration continue et déploiement continu

## Environnement de développement

- Éditeur : VS Code
- Langage : Python (3.14 en local, 3.12 dans la CI et l'image Docker — voir
  `docs/plan_correction_bugs.md` pour la raison de cet écart)
- Python est un langage interprété : il n'y a pas de compilateur à proprement
  parler, le fichier source est exécuté directement par l'interpréteur.
- Serveur d'application : Uvicorn (serveur ASGI qui fait tourner FastAPI)
- Gestion de sources : Git, dépôt hébergé sur GitHub

## Protocole d'intégration continue

Déclenché à chaque `push` ou `pull request` (voir
`.github/workflows/ci.yml`), le job `lint-and-test` :

1. récupère le code (`actions/checkout`),
2. installe Python 3.12 et les dépendances (`requirements.txt`),
3. lance le lint (`ruff check .`),
4. lance les tests avec couverture (`pytest --cov=app`).

Si une seule de ces étapes échoue, le workflow s'arrête en erreur : ça évite
de fusionner du code qui casse les tests ou qui ne respecte pas les règles de
style.

## Protocole de déploiement continu

Un deuxième job, `build-docker-image`, ne se lance que si `lint-and-test` a
réussi (`needs: lint-and-test`). Il construit l'image Docker de
l'application et la tague avec le hash du commit (`skillmatch:${{
github.sha }}`), ce qui donne une image prête à être déployée pour chaque
version validée du code.

Séquence complète à chaque push :

```
push → checkout → install deps → lint → tests → (si OK) build image Docker
```

Limite assumée : le projet n'a pas de serveur de production ni de registre
Docker distant, donc l'image est construite mais n'est pas poussée ni
déployée automatiquement sur un serveur. Pour aller plus loin, l'étape
suivante serait un `docker push` vers un registre (Docker Hub, GitHub
Container Registry) suivi d'un redéploiement automatique.

## Critères de qualité et de performance

**Qualité du code**

- `ruff check .` doit passer sans erreur avant tout merge (règles E =
  erreurs de style, F = bugs potentiels/imports inutilisés, I = tri des
  imports, voir `pyproject.toml`).
- Couverture de tests visée : au moins 90 % des lignes de `app/`. Couverture
  actuelle : 95 % (`pytest --cov=app`).

**Performance / contraintes fonctionnelles**

- Taille max d'un CV uploadé : 5 Mo (au-delà, rejet immédiat en 413 plutôt
  que de laisser un traitement long démarrer inutilement).
- Pas de test de charge formel : le projet est pensé pour un usage local,
  mono-utilisateur, pas pour un trafic concurrent important. C'est une
  limite assumée compte tenu du périmètre du projet.
