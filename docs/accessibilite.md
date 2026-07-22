# Accessibilité

## Référentiel choisi

**RGAA** (Référentiel Général d'Amélioration de l'Accessibilité), version 4.1.

Deux référentiels étaient envisageables : RGAA et OPQUAST. J'ai choisi RGAA
parce que c'est le référentiel officiel français dédié spécifiquement à
l'accessibilité web (OPQUAST couvre plus largement la qualité web en
général, l'accessibilité n'y est qu'une partie parmi d'autres). RGAA donne
des critères concrets et vérifiables, ce qui correspond à ce qu'on peut
démontrer sur un petit projet comme SkillMatch.

## Ce qui a été fait, par rapport aux critères RGAA

| Thématique RGAA | Ce qui est fait dans SkillMatch |
|---|---|
| Couleurs et contrastes | Contrastes vérifiés par calcul (texte ~15:1, boutons ~7.5:1), largement au-dessus du minimum RGAA/WCAG AA (4.5:1). Voir `app/static/style.css`. |
| Formulaires | Chaque champ (`file`, `search`) a un `<label>` associé via `for`/`id`. |
| Structuration de l'information | Hiérarchie de titres `h1`/`h2` respectée, tableau de résultats avec `<caption>` et `<th scope="col">`. |
| Navigation au clavier | Contour de focus visible et décalé (`outline-offset`) sur tous les éléments interactifs, vérifié à la main (navigation à la tabulation). |
| Scripts | Pas de JavaScript dans l'interface, donc pas de risque de piège au clavier ou de contenu inaccessible lié à du JS. |
| Images | Non applicable : l'interface n'affiche aucune image (pas d'attribut `alt` à gérer). |
| Langue de la page | `lang="fr"` déclaré sur la balise `<html>`. |

## Limites

Pas d'audit RGAA complet réalisé avec un outil dédié (ex : Wave, axe
DevTools) ni avec un vrai lecteur d'écran. Les points ci-dessus ont été
vérifiés un par un, manuellement, pendant le développement — voir
`docs/cahier_de_recettes.md`, scénario 10.
