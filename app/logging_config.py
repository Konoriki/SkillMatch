"""Configuration de la journalisation applicative de SkillMatch.

Format texte structuré (un événement par ligne, champs clé=valeur) plutôt que
du JSON : suffisant pour un usage local/petite échelle, et lisible directement
dans la console ou un fichier de log sans outil supplémentaire.
"""
import logging
import sys

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def setup_logging(level: int = logging.INFO) -> None:
    """Initialise la config de logging racine de l'application (idempotent)."""
    root = logging.getLogger()
    if root.handlers:
        return  # déjà configuré (évite les doublons si appelé plusieurs fois, ex. tests)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    root.addHandler(handler)
    root.setLevel(level)
