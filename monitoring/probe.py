"""Sonde de supervision de SkillMatch.

Interroge périodiquement GET /health et journalise deux indicateurs :
- disponibilité (le endpoint répond-il avec un statut 200 ?)
- temps de réponse (en millisecondes)

En cas d'échec (statut != 200, timeout, erreur réseau), une entrée de niveau
CRITICAL est écrite : c'est la modalité de signalement retenue pour ce
projet local (journal consultable dans monitoring/probe.log, et code de
sortie non nul en mode --once pour permettre le branchement d'un
ordonnanceur externe, ex. Tâche planifiée Windows ou cron, qui déclenche une
notification à partir de ce code retour).

Usage :
    python monitoring/probe.py                          # boucle toutes les 30s
    python monitoring/probe.py --interval 10             # boucle toutes les 10s
    python monitoring/probe.py --once                    # une seule vérification (ex. cron)
    python monitoring/probe.py --url http://host:8000/health

Note : préférer 127.0.0.1 à localhost dans l'URL. Sur certaines machines
Windows, la résolution de "localhost" tente d'abord l'IPv6 avant de
retomber sur l'IPv4, ce qui ajoute jusqu'à ~2s de latence artificielle à
chaque mesure de temps de réponse.
"""
import argparse
import logging
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "probe.log"

logger = logging.getLogger("skillmatch.probe")


def setup_logging() -> None:
    if logger.handlers:
        return
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"
    )
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)


def check_once(url: str, timeout: float = 5.0) -> bool:
    """Effectue une vérification unique. Retourne True si l'app est disponible."""
    start = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            elapsed_ms = (time.monotonic() - start) * 1000
            if response.status == 200:
                logger.info(
                    "disponible statut=%s temps_reponse_ms=%.1f", response.status, elapsed_ms
                )
                return True
            logger.critical(
                "ALERTE indisponible statut=%s temps_reponse_ms=%.1f", response.status, elapsed_ms
            )
            return False
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        logger.critical(
            "ALERTE indisponible statut=%s temps_reponse_ms=%.1f", exc.code, elapsed_ms
        )
        return False
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        logger.critical("ALERTE indisponible erreur=%s temps_reponse_ms=%.1f", exc, elapsed_ms)
        return False


def run_loop(url: str, interval: float) -> None:
    logger.info("demarrage sonde url=%s intervalle_s=%s", url, interval)
    while True:
        check_once(url)
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sonde de supervision SkillMatch")
    parser.add_argument(
        "--url", default="http://127.0.0.1:8000/health", help="URL du endpoint /health"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=30.0,
        help="secondes entre deux vérifications (mode boucle)",
    )
    parser.add_argument(
        "--once", action="store_true", help="une seule vérification puis quitte (code retour 0/1)"
    )
    args = parser.parse_args()

    setup_logging()

    if args.once:
        ok = check_once(args.url)
        sys.exit(0 if ok else 1)

    try:
        run_loop(args.url, args.interval)
    except KeyboardInterrupt:
        logger.info("arret sonde (interruption utilisateur)")


if __name__ == "__main__":
    main()
