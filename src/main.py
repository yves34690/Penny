"""
Script principal ETL Pennylane → PostgreSQL
Extrait les données de l'API, applique transformations basiques et charge dans PostgreSQL
"""

import sys
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd

# Import des modules locaux
from config_loader import load_full_config, validate_config
from pennylane_api import PennylaneAPI
from transformations import DataTransformer
from database import PostgresDatabase

# Configuration du logging
def setup_logging(config: dict):
    """Configure le système de logging"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', 'logs/pennylane_etl.log')

    # Créer le dossier logs si nécessaire
    Path(log_file).parent.mkdir(exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)


def extract_data(api: PennylaneAPI, endpoint_config: dict, last_sync: datetime = None) -> pd.DataFrame:
    """
    Extrait les données d'un endpoint Pennylane

    Args:
        api: Client API Pennylane
        endpoint_config: Configuration de l'endpoint
        last_sync: Date de dernière synchronisation pour extraction incrémentielle

    Returns:
        DataFrame avec les données extraites
    """
    endpoint = endpoint_config['endpoint']
    table_name = endpoint_config['table_name']
    is_incremental = endpoint_config.get('incremental', False)
    date_field = endpoint_config.get('date_field')

    logger.info(f"Extraction de {table_name} depuis {endpoint}")

    try:
        if is_incremental and last_sync and date_field:
            # Extraction incrémentielle
            data = api.get_incremental_data(endpoint, last_sync, date_field)
            logger.info(f"Extraction incrémentielle: {len(data)} nouveaux enregistrements")
        else:
            # Extraction complète
            data = api.get_paginated_data(endpoint)
            logger.info(f"Extraction complète: {len(data)} enregistrements")

        # Convertir en DataFrame
        if data:
            df = pd.DataFrame(data)
            logger.info(f"DataFrame créé: {len(df)} lignes, {len(df.columns)} colonnes")
            return df
        else:
            logger.warning(f"Aucune donnée extraite pour {table_name}")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Erreur extraction {table_name}: {e}")
        raise


def transform_data(df: pd.DataFrame, transformer: DataTransformer, table_name: str) -> pd.DataFrame:
    """
    Applique les transformations basiques sur les données

    Args:
        df: DataFrame à transformer
        transformer: Transformateur
        table_name: Nom de la table

    Returns:
        DataFrame transformé
    """
    if df.empty:
        return df

    logger.info(f"Transformation de {table_name}")

    try:
        df = transformer.basic_transform(df, table_name)
        return df
    except Exception as e:
        logger.error(f"Erreur transformation {table_name}: {e}")
        raise


def load_data(df: pd.DataFrame, db: PostgresDatabase, table_name: str,
             if_exists: str = 'replace') -> int:
    """
    Charge les données dans PostgreSQL

    Args:
        df: DataFrame à charger
        db: Connexion database
        table_name: Nom de la table
        if_exists: Mode de chargement

    Returns:
        Nombre de lignes chargées
    """
    if df.empty:
        logger.warning(f"Pas de données à charger pour {table_name}")
        return 0

    logger.info(f"Chargement de {table_name} dans PostgreSQL")

    try:
        rows_loaded = db.load_dataframe(df, table_name, if_exists=if_exists)
        db.update_sync_metadata(table_name, rows_loaded)
        return rows_loaded
    except Exception as e:
        logger.error(f"Erreur chargement {table_name}: {e}")
        raise


def process_endpoint(api: PennylaneAPI, db: PostgresDatabase, transformer: DataTransformer,
                    endpoint_config: dict, mode: str = 'full') -> dict:
    """
    Traite un endpoint complet (Extract, Transform, Load)

    Args:
        api: Client API
        db: Connexion database
        transformer: Transformateur
        endpoint_config: Configuration de l'endpoint
        mode: 'full' ou 'incremental'

    Returns:
        Dictionnaire avec résultats
    """
    table_name = endpoint_config['table_name']
    start_time = datetime.now()

    logger.info(f"{'='*60}")
    logger.info(f"Traitement de {table_name}")
    logger.info(f"{'='*60}")

    result = {
        'table_name': table_name,
        'status': 'success',
        'records_extracted': 0,
        'records_loaded': 0,
        'error_message': None,
        'execution_time': 0
    }

    try:
        # 1. EXTRACT
        last_sync = db.get_last_sync_date(table_name) if mode == 'incremental' else None
        df = extract_data(api, endpoint_config, last_sync)
        result['records_extracted'] = len(df)

        if df.empty:
            logger.info(f"Aucune donnée à traiter pour {table_name}")
            result['status'] = 'no_data'
            return result

        # 2. TRANSFORM
        df = transform_data(df, transformer, table_name)

        # 3. LOAD
        if_exists = 'replace' if mode == 'full' else 'append'
        rows_loaded = load_data(df, db, table_name, if_exists=if_exists)
        result['records_loaded'] = rows_loaded

        # Temps d'exécution
        duration = (datetime.now() - start_time).total_seconds()
        result['execution_time'] = duration

        logger.info(f"✓ {table_name} traité avec succès ({duration:.2f}s)")

    except Exception as e:
        result['status'] = 'failed'
        result['error_message'] = str(e)
        logger.error(f"✗ Échec traitement {table_name}: {e}")

    finally:
        # Log dans la base
        db.log_etl_execution(
            table_name=result['table_name'],
            records_extracted=result['records_extracted'],
            records_loaded=result['records_loaded'],
            status=result['status'],
            error_message=result['error_message'],
            execution_time=result['execution_time']
        )

    return result


def main(mode: str = 'full'):
    """
    Fonction principale d'exécution ETL

    Args:
        mode: 'full' pour extraction complète, 'incremental' pour incrémentielle
    """
    print("="*80)
    print("ETL Pennylane → PostgreSQL")
    print(f"Mode: {mode.upper()}")
    print(f"Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

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

    logger.info(f"Démarrage ETL en mode {mode}")

    # Initialiser les composants
    api = PennylaneAPI(
        api_key=config['pennylane_api']['api_key'],
        base_url=config['pennylane_api']['base_url'],
        rate_limit=config['pennylane_api']['rate_limit']['requests_per_second']
    )

    transformer = DataTransformer(config)

    # Test connexion API
    if not api.test_connection():
        logger.error("Impossible de se connecter à l'API Pennylane")
        sys.exit(1)

    # Connexion à la base de données
    try:
        with PostgresDatabase(config) as db:
            logger.info("Connexion PostgreSQL établie")

            # Traiter chaque endpoint configuré
            endpoints = config['endpoints']['enabled']
            results = []

            for endpoint_config in endpoints:
                result = process_endpoint(api, db, transformer, endpoint_config, mode)
                results.append(result)

            # Résumé
            print("\n" + "="*80)
            print("RÉSUMÉ DE L'EXÉCUTION")
            print("="*80)

            total_extracted = sum(r['records_extracted'] for r in results)
            total_loaded = sum(r['records_loaded'] for r in results)
            success = sum(1 for r in results if r['status'] == 'success')
            failed = sum(1 for r in results if r['status'] == 'failed')

            print(f"Tables traitées: {len(results)}")
            print(f"  ✓ Succès: {success}")
            print(f"  ✗ Échecs: {failed}")
            print(f"Enregistrements extraits: {total_extracted:,}")
            print(f"Enregistrements chargés: {total_loaded:,}")

            print("\nDétail par table:")
            for r in results:
                status_icon = "✓" if r['status'] == 'success' else "✗"
                print(f"  {status_icon} {r['table_name']}: "
                     f"{r['records_extracted']:,} extraits, "
                     f"{r['records_loaded']:,} chargés "
                     f"({r['execution_time']:.2f}s)")

            print("="*80)
            logger.info("ETL terminé")

    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # Par défaut: extraction complète
    # Passer 'incremental' en argument pour extraction incrémentielle
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'

    if mode not in ['full', 'incremental']:
        print("Mode invalide. Utilisez 'full' ou 'incremental'")
        sys.exit(1)

    main(mode)
