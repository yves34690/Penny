"""
Scheduler orchestrateur Pennylane -> PostgreSQL

Architecture hybride:
- Sync incrementale toutes les 2h (rapide, quelques secondes)
- Full reload 1x par jour a 3h du matin (complet, garantit coherence)
- Notebooks Jupyter restent disponibles pour usage manuel/debug

Le full reload quotidien garantit la coherence meme si un changelog est
rate (les changelogs ne remontent que 4 semaines max).
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
import schedule

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/notebook_scheduler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class NotebookScheduler:
    """Orchestrateur de synchronisation Pennylane"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent

        # Config notebooks (garde pour usage manuel/debug)
        self.notebooks_dir = self.base_dir / "data" / "API Publique"
        self.output_dir = self.base_dir / "data" / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("[INIT] Scheduler Pennylane initialise")
        logger.info(f"[INIT] Mode: sync incrementale API v2 + full reload quotidien")

    # ========================================================================
    # SYNC INCREMENTALE (API v2 + changelogs)
    # ========================================================================

    def run_incremental_sync(self):
        """Execute la sync incrementale via API v2 (rapide)"""
        logger.info("=" * 80)
        logger.info(
            f"[CRON] SYNC INCREMENTALE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        logger.info("=" * 80)

        try:
            from src.incremental_sync import run_sync

            success = run_sync(force_full=False)
            if success:
                logger.info("[CRON] Sync incrementale terminee avec succes")
            else:
                logger.error("[CRON] Sync incrementale terminee avec des erreurs")
        except Exception as e:
            logger.error(f"[CRON] Erreur sync incrementale: {e}")

    def run_full_sync(self):
        """Execute un full reload complet via API v2"""
        logger.info("=" * 80)
        logger.info(
            f"[CRON] FULL RELOAD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        logger.info("=" * 80)

        try:
            from src.incremental_sync import run_sync

            success = run_sync(force_full=True)
            if success:
                logger.info("[CRON] Full reload termine avec succes")
            else:
                logger.error("[CRON] Full reload termine avec des erreurs")
        except Exception as e:
            logger.error(f"[CRON] Erreur full reload: {e}")

    # ========================================================================
    # SCHEDULER
    # ========================================================================

    def start(self):
        """Demarre le scheduler"""
        logger.info("=" * 80)
        logger.info("[DEMARRAGE] Scheduler Pennylane v2")
        logger.info("[DEMARRAGE] Sync incrementale toutes les 5 min")
        logger.info("[DEMARRAGE] Full reload quotidien a 03:00")
        logger.info("=" * 80)

        # Execution initiale (full pour peupler les tables au premier lancement)
        logger.info("[CRON] Execution initiale (full reload)...")
        self.run_full_sync()

        # Planifier executions futures
        schedule.every(5).minutes.do(self.run_incremental_sync)
        schedule.every().day.at("03:00").do(self.run_full_sync)

        logger.info("[CRON] Planification activee:")
        logger.info("[CRON]   - Sync incrementale: toutes les 2h")
        logger.info("[CRON]   - Full reload: tous les jours a 03:00")
        logger.info("[CRON] Ctrl+C pour arreter")

        # Boucle infinie
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("[ARRET] Scheduler arrete par l'utilisateur")
            sys.exit(0)


def main():
    """Point d'entree du scheduler"""
    scheduler = NotebookScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
