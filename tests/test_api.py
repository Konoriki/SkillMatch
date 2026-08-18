"""Tests pour les routes de l'API FastAPI."""
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app
from tests.test_extraction import make_pdf

# Base en mémoire pour les tests. StaticPool garde une seule connexion
# ouverte, sinon chaque session ":memory:" repartirait sur une base vide.
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(test_engine)


def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)


def test_health_returns_ok_status():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["checks"]["database"] == "ok"
    assert "timestamp" in data


def test_upload_valid_pdf_returns_extracted_text():
    pdf_bytes = make_pdf(["Competences: Python, SQL"])
    response = client.post(
        "/upload",
        files={"file": ("cv.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "cv.pdf"
    assert "Python" in data["text_preview"]
    assert set(data["skills"]) == {"Python", "SQL"}


def test_upload_rejects_non_pdf_file():
    response = client.post(
        "/upload",
        files={"file": ("cv.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_rejects_spoofed_content_type():
    """Content-Type déclaré à 'application/pdf' mais octets réels non conformes."""
    response = client.post(
        "/upload",
        files={"file": ("faux.pdf", b"ceci n'est pas un PDF", "application/pdf")},
    )
    assert response.status_code == 400


def test_upload_rejects_corrupted_pdf():
    """En-tête PDF valide mais contenu illisible (pas de /Root)."""
    corrupted = b"%PDF-1.4\ncontenu volontairement corrompu, pas une structure PDF valide"
    response = client.post(
        "/upload",
        files={"file": ("corrompu.pdf", corrupted, "application/pdf")},
    )
    assert response.status_code == 400


def test_upload_rejects_file_exceeding_max_size():
    oversized = b"%PDF-1.4\n" + b"0" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/upload",
        files={"file": ("gros.pdf", oversized, "application/pdf")},
    )
    assert response.status_code == 413


def test_upload_with_html_accept_redirects_to_home():
    pdf_bytes = make_pdf(["Competences: Elixir"])
    response = client.post(
        "/upload",
        files={"file": ("cv_elixir.pdf", pdf_bytes, "application/pdf")},
        headers={"accept": "text/html"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_index_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "SkillMatch" in response.text


def test_index_lists_uploaded_candidat():
    pdf_bytes = make_pdf(["Competences: Rust"])
    client.post("/upload", files={"file": ("cv_rust.pdf", pdf_bytes, "application/pdf")})

    response = client.get("/")

    assert "cv_rust.pdf" in response.text
    assert "Rust" in response.text


def test_search_by_competence_filters_results():
    pdf_kotlin = make_pdf(["Competences: Kotlin"])
    client.post("/upload", files={"file": ("cv_kotlin.pdf", pdf_kotlin, "application/pdf")})
    pdf_swift = make_pdf(["Competences: Swift"])
    client.post("/upload", files={"file": ("cv_swift.pdf", pdf_swift, "application/pdf")})

    response = client.get("/", params={"q": "Kotlin"})

    assert "cv_kotlin.pdf" in response.text
    assert "cv_swift.pdf" not in response.text
