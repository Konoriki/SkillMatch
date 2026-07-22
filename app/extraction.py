"""Extraction du texte d'un PDF et détection des compétences dedans."""
import re
from io import BytesIO

import pdfplumber

from app.skills import SKILLS_DICTIONARY


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Récupère tout le texte d'un PDF, page par page."""
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        pages_text = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages_text).strip()


def detect_skills(text: str) -> list[str]:
    """Cherche dans le texte les compétences connues du dictionnaire.

    On ne peut pas utiliser \\b (frontière de mot classique) car des
    compétences comme "C++", ".NET" ou "Vue.js" contiennent des caractères
    spéciaux. La regex vérifie juste qu'il n'y a pas de lettre/chiffre
    collé avant ou après le mot trouvé, ce qui évite par exemple de
    détecter "Java" à l'intérieur de "JavaScript".
    """
    found: list[str] = []
    for category_skills in SKILLS_DICTIONARY.values():
        for skill in category_skills:
            pattern = r"(?<![\w.+#-])" + re.escape(skill) + r"(?![\w.+#-])"
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.append(skill)
    return found
