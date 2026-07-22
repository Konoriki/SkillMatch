# Cahier de recettes

Scénarios de test fonctionnels. La plupart sont automatisés (voir `tests/`,
lancés avec `pytest`), certains ont aussi été vérifiés à la main dans le
navigateur.

| # | Scénario | Résultat attendu | Résultat obtenu |
|---|----------|-------------------|-------------------|
| 1 | Upload d'un CV PDF valide contenant des compétences connues | Le candidat apparaît dans la liste avec ses compétences détectées | Conforme (`test_upload_valid_pdf_returns_extracted_text`, vérifié aussi à la main : upload d'un CV test avec Python/Docker/React/PostgreSQL, les 4 compétences ressortent) |
| 2 | Upload d'un fichier qui n'est pas un PDF (ex : `.txt`) | Rejeté avec une erreur 400 | Conforme (`test_upload_rejects_non_pdf_file`) |
| 3 | Upload d'un fichier renommé en `.pdf` mais avec un `Content-Type` falsifié | Rejeté (le contenu réel du fichier est vérifié, pas juste l'en-tête déclaré) | Conforme (`test_upload_rejects_spoofed_content_type`) |
| 4 | Upload d'un PDF corrompu (en-tête valide mais structure illisible) | Rejeté proprement en 400, pas de crash serveur | Conforme (`test_upload_rejects_corrupted_pdf`) |
| 5 | Upload d'un fichier de plus de 5 Mo | Rejeté en 413 | Conforme (`test_upload_rejects_file_exceeding_max_size`) |
| 6 | Recherche par compétence exacte (ex : "Python") | Seuls les candidats ayant cette compétence s'affichent | Conforme (`test_search_by_competence_filters_results`, vérifié à la main aussi) |
| 7 | Recherche insensible à la casse (ex : "react" au lieu de "React") | Le candidat correspondant est trouvé quand même | Conforme (`test_search_candidats_by_competence_is_case_insensitive`, vérifié à la main dans le navigateur) |
| 8 | Recherche sur une compétence que personne ne possède | Message "Aucun candidat pour cette compétence" | Conforme (vérifié à la main, ex : recherche "Rust" sur un candidat qui n'a que "React, Docker...") |
| 9 | Deux candidats différents ont la même compétence | La compétence n'est stockée qu'une seule fois en base, pas de doublon | Conforme (`test_add_candidat_reuses_existing_competence`) |
| 10 | Navigation au clavier (tabulation) dans le formulaire | Le focus est visible sur chaque champ/bouton | Conforme, vérifié à la main (contour de focus visible sur le champ fichier) |
| 11 | Chargement de la feuille de style | La page ne s'affiche pas en HTML brut sans mise en forme | Conforme, `GET /static/style.css` renvoie 200 |

## Ce qui n'est pas couvert pour l'instant

- Pas de test automatisé sur le contraste des couleurs ou le rendu avec un vrai lecteur d'écran (vérifié seulement "à l'œil" et par calcul de contraste, voir le README).
- Pas de CV scanné (image) testé : `pdfplumber` ne fait pas d'OCR, un tel PDF donnerait un texte vide et donc aucune compétence détectée (comportement attendu, mais pas un vrai cas de test ici).
