"""Base SQLite et modèles de données (SQLModel).

Un candidat peut avoir plusieurs compétences, et une compétence peut être
partagée par plusieurs candidats : c'est une relation many-to-many, gérée
par la table CandidatCompetenceLink. Ça évite de recréer "Python" en base
à chaque nouveau candidat qui sait coder en Python.
"""
from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

DB_PATH = Path(__file__).resolve().parent.parent / "skillmatch.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, echo=False)


class CandidatCompetenceLink(SQLModel, table=True):
    """Table d'association many-to-many entre un candidat et ses compétences."""

    candidat_id: int | None = Field(default=None, foreign_key="candidat.id", primary_key=True)
    competence_id: int | None = Field(default=None, foreign_key="competence.id", primary_key=True)


class Competence(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nom: str = Field(unique=True, index=True)

    candidats: list["Candidat"] = Relationship(
        back_populates="competences", link_model=CandidatCompetenceLink
    )


class Candidat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nom_fichier: str
    date_ajout: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    competences: list[Competence] = Relationship(
        back_populates="candidats", link_model=CandidatCompetenceLink
    )


def create_db_and_tables() -> None:
    """Crée les tables si elles n'existent pas déjà."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dépendance FastAPI fournissant une session ; remplaçable dans les tests."""
    with Session(engine) as session:
        yield session


def add_candidat(session: Session, nom_fichier: str, noms_competences: list[str]) -> Candidat:
    """Enregistre un candidat et associe ses compétences (réutilise celles qui existent déjà).

    La vérification puis création d'une compétence n'est pas atomique : si
    une autre requête crée la même compétence entre-temps, le commit lève
    une IntegrityError (contrainte unique sur Competence.nom). Dans ce cas
    on retente une fois, la compétence étant alors trouvée par la relecture
    (voir issue #2).
    """
    for tentative in range(2):
        competences = []
        for nom in noms_competences:
            competence = session.exec(select(Competence).where(Competence.nom == nom)).first()
            if competence is None:
                competence = Competence(nom=nom)
            competences.append(competence)

        candidat = Candidat(nom_fichier=nom_fichier, competences=competences)
        session.add(candidat)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            if tentative == 1:
                raise
            continue
        session.refresh(candidat)
        return candidat


def _escape_like_wildcards(value: str) -> str:
    """Échappe les métacaractères SQL % et _ pour que ILIKE fasse une recherche exacte.

    Sans ça, une recherche comme "P%" matche aussi "PHP" en plus de "Python"
    (voir issue #1).
    """
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_candidats_by_competence(session: Session, nom_competence: str) -> list[Candidat]:
    """Retourne les candidats possédant la compétence donnée.

    Recherche exacte, insensible à la casse : les métacaractères SQL % et _
    saisis par l'utilisateur sont échappés (voir _escape_like_wildcards).
    """
    statement = (
        select(Candidat)
        .join(CandidatCompetenceLink)
        .join(Competence)
        .where(Competence.nom.ilike(_escape_like_wildcards(nom_competence), escape="\\"))
        .distinct()
    )
    return list(session.exec(statement).all())
