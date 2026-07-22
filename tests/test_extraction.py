"""Tests pour l'extraction de texte PDF."""
from io import BytesIO

from reportlab.pdfgen import canvas

from app.extraction import detect_skills, extract_text_from_pdf


def make_pdf(text_lines: list[str]) -> bytes:
    """Génère un PDF minimal en mémoire contenant les lignes de texte données."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    y = 800
    for line in text_lines:
        pdf.drawString(50, y, line)
        y -= 20
    pdf.save()
    return buffer.getvalue()


def test_extract_text_from_pdf_returns_content():
    pdf_bytes = make_pdf(["Jean Dupont", "Competences: Python, SQL, Docker"])
    text = extract_text_from_pdf(pdf_bytes)
    assert "Jean Dupont" in text
    assert "Python" in text


def test_extract_text_from_pdf_empty_pdf_returns_empty_string():
    pdf_bytes = make_pdf([])
    text = extract_text_from_pdf(pdf_bytes)
    assert text == ""


def test_detect_skills_finds_known_skills():
    text = "Experience: Python, SQL, Docker"
    skills = detect_skills(text)
    assert set(skills) == {"Python", "SQL", "Docker"}


def test_detect_skills_is_case_insensitive():
    skills = detect_skills("je maitrise python et docker")
    assert "Python" in skills
    assert "Docker" in skills


def test_detect_skills_ignores_unknown_words():
    skills = detect_skills("Cuisine, Guitare, Photographie")
    assert skills == []


def test_detect_skills_avoids_partial_word_matches():
    """"Java" ne doit pas être détecté à l'intérieur de "JavaScript"."""
    skills = detect_skills("Maitrise de JavaScript")
    assert "JavaScript" in skills
    assert "Java" not in skills
