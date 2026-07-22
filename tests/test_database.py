"""Tests pour la couche base de données."""
import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from app.database import Competence, add_candidat, search_candidats_by_competence


@pytest.fixture
def session():
    """Base SQLite en mémoire, recréée à chaque test pour l'isolation."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_add_candidat_creates_candidat_and_competences(session):
    candidat = add_candidat(session, "cv_jean.pdf", ["Python", "SQL"])
    assert candidat.id is not None
    assert {c.nom for c in candidat.competences} == {"Python", "SQL"}


def test_add_candidat_reuses_existing_competence(session):
    add_candidat(session, "cv_jean.pdf", ["Python"])
    add_candidat(session, "cv_marie.pdf", ["Python", "Docker"])

    competences_python = session.exec(
        select(Competence).where(Competence.nom == "Python")
    ).all()
    assert len(competences_python) == 1


def test_search_candidats_by_competence_returns_matching_candidats(session):
    add_candidat(session, "cv_jean.pdf", ["Python", "Docker"])
    add_candidat(session, "cv_marie.pdf", ["Java"])

    resultats = search_candidats_by_competence(session, "Python")

    assert len(resultats) == 1
    assert resultats[0].nom_fichier == "cv_jean.pdf"


def test_search_candidats_by_competence_is_case_insensitive(session):
    add_candidat(session, "cv_jean.pdf", ["Python"])

    resultats = search_candidats_by_competence(session, "python")

    assert len(resultats) == 1


def test_search_candidats_by_competence_returns_empty_list_when_no_match(session):
    add_candidat(session, "cv_jean.pdf", ["Python"])

    resultats = search_candidats_by_competence(session, "Rust")

    assert resultats == []
