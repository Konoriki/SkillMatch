"""Points d'entrée FastAPI de SkillMatch."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import (
    Candidat,
    add_candidat,
    create_db_and_tables,
    get_session,
    search_candidats_by_competence,
)
from app.extraction import detect_skills, extract_text_from_pdf

# Taille max raisonnable pour un CV, et vérif du vrai contenu du fichier
# (le Content-Type envoyé par le navigateur peut être faux).
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 Mo
PDF_MAGIC_BYTES = b"%PDF-"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="SkillMatch", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/")
def index(request: Request, q: str | None = None, session: Session = Depends(get_session)):
    """Page d'accueil : formulaire d'upload, formulaire de recherche, liste des candidats."""
    if q:
        candidats = search_candidats_by_competence(session, q)
    else:
        candidats = session.exec(select(Candidat)).all()

    return templates.TemplateResponse(
        request, "index.html", {"candidats": candidats, "query": q}
    )


@app.post("/upload")
async def upload_cv(
    request: Request,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    """Reçoit un CV PDF, extrait le texte, détecte les compétences et enregistre le candidat.

    Répond en JSON pour un appel API. Si la requête vient du formulaire HTML
    du navigateur, on redirige plutôt vers l'accueil (on regarde l'en-tête
    Accept pour faire la différence).
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF.")

    pdf_bytes = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(pdf_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Le fichier dépasse la taille maximale autorisée (5 Mo).",
        )

    if not pdf_bytes.startswith(PDF_MAGIC_BYTES):
        raise HTTPException(status_code=400, detail="Le fichier n'est pas un PDF valide.")

    try:
        text = extract_text_from_pdf(pdf_bytes)
    except Exception as exc:
        # un PDF corrompu ou protégé fait planter pdfplumber avec des erreurs
        # différentes selon les cas : on les traite toutes comme une erreur
        # de saisie (400) plutôt que de laisser planter le serveur (500).
        raise HTTPException(
            status_code=400, detail="Impossible de lire ce PDF (fichier corrompu ou protégé)."
        ) from exc

    skills = detect_skills(text)
    candidat = add_candidat(session, file.filename, skills)

    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/", status_code=303)

    return {
        "candidat_id": candidat.id,
        "filename": candidat.nom_fichier,
        "text_length": len(text),
        "text_preview": text[:500],
        "skills": skills,
    }
