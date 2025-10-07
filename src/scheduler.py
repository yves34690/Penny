"""
Planificateur automatique pour exécution ETL toutes les X minutes
"""

import schedule
import time
import logging
from datetime import datetime
import sys
from pathlib import Path

# Import du script principal
from config_loader import load_full_config, validate_config
from main import main, setup_logging

logger = logging.getLogger(__name__)


class ETLScheduler:
    """Planificateur pour ETL Pennylane"""

    def __init__(self, interval_minutes: int = 10):
        """
        Initialise le planificateur

        Args:
            interval_minutes: Intervalle d'exécution en minutes
        """
        self.interval_minutes = interval_minutes
        self.is_running = False
        self.execution_count = 0
        self.last_execution = None

    def run_etl(self):
        """Exécute l'ETL en mode incrémentiel"""
        self.execution_count += 1
        self.last_execution = datetime.now()

        logger.info("="*80)
        logger.info(f"Exécution planifiée #{self.execution_count}")
        logger.info(f"Heure: {self.last_execution.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)

        try:
            # Exécuter ETL en mode incrémentiel
            main(mode='incremental')
            logger.info(f"✓ Exécution #{self.execution_count} terminée avec succès")

        except Exception as e:
            logger.error(f"✗ Erreur lors de l'exécution #{self.execution_count}: {e}")

    def start(self):
        """Démarre le planificateur"""
        print("="*80)
        print("PLANIFICATEUR ETL PENNYLANE")
        print("="*80)
        print(f"Intervalle: toutes les {self.interval_minutes} minutes")
        print(f"Mode: Extraction incrémentielle")
        print(f"Démarré à: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Prochaine exécution: dans {self.interval_minutes} minutes")
        print("="*80)
        print("\nAppuyez sur Ctrl+C pour arrêter\n")

        logger.info(f"Planificateur démarré (intervalle: {self.interval_minutes} min)")

        # Planifier l'exécution
        schedule.every(self.interval_minutes).minutes.do(self.run_etl)

        # Option: Exécuter immédiatement au démarrage
        # self.run_etl()

        self.is_running = True

        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Arrête le planificateur"""
        print("\n" + "="*80)
        print("ARRÊT DU PLANIFICATEUR")
        print("="*80)
        print(f"Nombre d'exécutions: {self.execution_count}")
        if self.last_execution:
            print(f"Dernière exécution: {self.last_execution.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        logger.info(f"Planificateur arrêté après {self.execution_count} exécutions")
        self.is_running = False


def main_scheduler():
    """Point d'entrée principal du planificateur"""
    # Charger configuration depuis .env et config.json
    try:
        config = load_full_config()
        validate_config(config)
        setup_logging(config)
        logger.info("✓ Configuration chargée et validée")
    except ValueError as e:
        print(f"✗ Erreur de configuration: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Erreur chargement configuration: {e}")
        sys.exit(1)

    # Récupérer l'intervalle depuis la config
    scheduler_config = config.get('scheduler', {})
    interval = scheduler_config.get('interval_minutes', 10)

    if not scheduler_config.get('enabled', True):
        print("⚠ Planificateur désactivé dans la configuration")
        logger.warning("Planificateur désactivé dans .env")
        sys.exit(0)

    # Démarrer le planificateur
    scheduler = ETLScheduler(interval_minutes=interval)
    scheduler.start()


if __name__ == '__main__':
    main_scheduler()
