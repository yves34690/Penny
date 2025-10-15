"""
Scheduler orchestrateur de notebooks Pennylane
Exécute automatiquement les notebooks toutes les 2 heures

Architecture:
- Source unique: Les notebooks Jupyter
- Modifications dans notebooks = automatiquement appliquées
- Résultats exécution sauvegardés dans data/outputs/

Workflow utilisateur:
1. Modifier notebook (ajout colonnes, transformations)
2. Tester manuellement dans Jupyter
3. Laisser scheduler automatiser l'exécution
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
import schedule
import papermill as pm

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/notebook_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NotebookScheduler:
    """Orchestrateur de notebooks Pennylane"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.notebooks_dir = self.base_dir / "data" / "API Publique"
        self.output_dir = self.base_dir / "data" / "outputs"

        # Créer dossier outputs
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configuration notebooks à exécuter
        self.notebooks = [
            # Tables API REST
            {
                'name': 'customers',
                'notebook': 'Import_customers.ipynb',
                'description': 'Clients (API REST)'
            },
            {
                'name': 'customer_invoices',
                'notebook': 'Import_customer_invoices.ipynb',
                'description': 'Factures clients (API REST)'
            },
            {
                'name': 'suppliers',
                'notebook': 'Import_suppliers.ipynb',
                'description': 'Fournisseurs (API REST)'
            },
            {
                'name': 'supplier_invoices',
                'notebook': 'Import_supplier_invoices.ipynb',
                'description': 'Factures fournisseurs (API REST)'
            },
            {
                'name': 'bank_transactions',
                'notebook': 'Import_bank_transactions.ipynb',
                'description': 'Transactions bancaires (API REST)'
            },

            # Tables Redshift Comptables
            {
                'name': 'analytical_ledger',
                'notebook': 'Import_analytical_ledger.ipynb',
                'description': 'Grand livre analytique (Redshift)'
            },
            {
                'name': 'general_ledger',
                'notebook': 'Import_general_ledger.ipynb',
                'description': 'Grand livre général (Redshift)'
            },
            {
                'name': 'trial_balance',
                'notebook': 'Import_trial_balance.ipynb',
                'description': 'Balance générale (Redshift)'
            },
            {
                'name': 'bank_accounts',
                'notebook': 'Import_bank_accounts.ipynb',
                'description': 'Comptes bancaires (Redshift)'
            },
            {
                'name': 'fiscal_years',
                'notebook': 'Import_fiscal_years.ipynb',
                'description': 'Exercices fiscaux (Redshift)'
            },
            {
                'name': 'tax_declarations',
                'notebook': 'Import_tax_declarations.ipynb',
                'description': 'Déclarations fiscales (Redshift)'
            },
            {
                'name': 'vat_declarations',
                'notebook': 'Import_vat_declarations.ipynb',
                'description': 'Déclarations TVA (Redshift)'
            }
        ]

        logger.info("[INIT] Notebook Scheduler initialise")
        logger.info(f"[INIT] Dossier notebooks: {self.notebooks_dir}")
        logger.info(f"[INIT] Dossier outputs: {self.output_dir}")
        logger.info(f"[INIT] {len(self.notebooks)} notebooks configures")

    def execute_notebook(self, notebook_config: dict) -> bool:
        """
        Exécute un notebook avec Papermill

        Args:
            notebook_config: Configuration du notebook (name, notebook, description)

        Returns:
            bool: True si succès, False si erreur
        """
        name = notebook_config['name']
        notebook_file = notebook_config['notebook']
        description = notebook_config['description']

        input_path = self.notebooks_dir / notebook_file

        # Vérifier existence
        if not input_path.exists():
            logger.warning(f"[SKIP] Notebook '{notebook_file}' introuvable")
            return False

        # Chemin output avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{name}_{timestamp}.ipynb"
        output_path = self.output_dir / output_filename

        try:
            logger.info(f"[EXECUTE] {description}")
            logger.info(f"[EXECUTE] Input: {notebook_file}")

            # Exécuter notebook avec papermill
            pm.execute_notebook(
                input_path=str(input_path),
                output_path=str(output_path),
                kernel_name='python3',
                progress_bar=False,
                log_output=True
            )

            logger.info(f"[OK] '{name}': Execution reussie")
            logger.info(f"[OK] Output sauvegarde: {output_filename}")
            return True

        except Exception as e:
            logger.error(f"[ERREUR] '{name}': {str(e)}")
            return False

    def run_sync(self):
        """Exécute synchronisation complète de tous les notebooks"""
        logger.info("=" * 80)
        logger.info(f"[SYNC] DEBUT synchronisation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

        start_time = time.time()
        success_count = 0
        error_count = 0

        for notebook_config in self.notebooks:
            success = self.execute_notebook(notebook_config)
            if success:
                success_count += 1
            else:
                error_count += 1

        duration = time.time() - start_time

        logger.info("=" * 80)
        logger.info(f"[SYNC] FIN synchronisation - Duree: {duration:.1f}s")
        logger.info(f"[SYNC] Succes: {success_count}/{len(self.notebooks)} | Erreurs: {error_count}")
        logger.info("=" * 80)

    def start(self):
        """Démarre le scheduler avec exécution toutes les 2 heures"""
        logger.info("=" * 80)
        logger.info("[DEMARRAGE] Notebook Scheduler Pennylane")
        logger.info("[DEMARRAGE] Actualisation toutes les 2 heures")
        logger.info(f"[DEMARRAGE] {len(self.notebooks)} notebooks a executer")
        logger.info("=" * 80)

        # Exécution initiale
        logger.info("[CRON] Execution initiale...")
        self.run_sync()

        # Planifier exécutions futures
        schedule.every(2).hours.do(self.run_sync)

        logger.info("[CRON] Planification activee - Prochaine execution dans 2h")
        logger.info("[CRON] Appuyez sur Ctrl+C pour arreter")

        # Boucle infinie
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Vérifier toutes les minutes
        except KeyboardInterrupt:
            logger.info("[ARRET] Scheduler arrete par l'utilisateur")
            sys.exit(0)

def main():
    """Point d'entrée du scheduler"""
    scheduler = NotebookScheduler()
    scheduler.start()

if __name__ == "__main__":
    main()
