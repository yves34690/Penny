"""
Module de gestion de la base de données PostgreSQL
Gère la connexion, création de tables et chargement de données
"""

import psycopg2
from psycopg2 import sql, extras
import pandas as pd
import logging
from typing import Dict, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PostgresDatabase:
    """Gestionnaire de connexion et opérations PostgreSQL"""

    def __init__(self, config: Dict):
        """
        Initialise la connexion PostgreSQL

        Args:
            config: Configuration de la base depuis config.json
        """
        self.config = config['database']
        self.schema = self.config.get('schema', 'pennylane')
        self.connection = None
        self.cursor = None

    def connect(self):
        """Établit la connexion à PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            self.connection.autocommit = False
            self.cursor = self.connection.cursor()
            logger.info("✓ Connexion PostgreSQL établie")
            return True

        except Exception as e:
            logger.error(f"✗ Erreur connexion PostgreSQL: {e}")
            raise

    def disconnect(self):
        """Ferme la connexion PostgreSQL"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Connexion PostgreSQL fermée")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type:
            self.connection.rollback()
            logger.error(f"Transaction annulée: {exc_val}")
        else:
            self.connection.commit()
        self.disconnect()

    def execute(self, query: str, params: Optional[tuple] = None):
        """
        Exécute une requête SQL

        Args:
            query: Requête SQL
            params: Paramètres de la requête
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Erreur requête SQL: {e}")
            raise

    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str,
                                   if_exists: str = 'replace'):
        """
        Crée une table PostgreSQL depuis un DataFrame

        Args:
            df: DataFrame source
            table_name: Nom de la table
            if_exists: 'replace', 'append' ou 'fail'
        """
        if df.empty:
            logger.warning(f"DataFrame vide, table {table_name} non créée")
            return

        full_table_name = f"{self.schema}.{table_name}"

        try:
            # Mapper types Pandas vers PostgreSQL
            type_mapping = {
                'int64': 'BIGINT',
                'Int64': 'BIGINT',
                'float64': 'DOUBLE PRECISION',
                'object': 'TEXT',
                'bool': 'BOOLEAN',
                'datetime64[ns]': 'TIMESTAMP',
                'datetime64[ns, UTC]': 'TIMESTAMP WITH TIME ZONE'
            }

            columns = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                pg_type = type_mapping.get(dtype, 'TEXT')
                col_safe = col.replace(' ', '_').replace('-', '_')
                columns.append(f'"{col_safe}" {pg_type}')

            columns_sql = ',\n    '.join(columns)

            if if_exists == 'replace':
                drop_query = f"DROP TABLE IF EXISTS {full_table_name} CASCADE"
                self.cursor.execute(drop_query)
                logger.info(f"Table {full_table_name} supprimée")

            create_query = f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    id SERIAL PRIMARY KEY,
                    {columns_sql},
                    _loaded_at TIMESTAMP DEFAULT NOW()
                )
            """

            self.cursor.execute(create_query)
            self.connection.commit()
            logger.info(f"✓ Table {full_table_name} créée ({len(df.columns)} colonnes)")

        except Exception as e:
            self.connection.rollback()
            logger.error(f"Erreur création table {table_name}: {e}")
            raise

    def load_dataframe(self, df: pd.DataFrame, table_name: str,
                      if_exists: str = 'append', batch_size: int = 1000):
        """
        Charge un DataFrame dans PostgreSQL

        Args:
            df: DataFrame à charger
            table_name: Nom de la table
            if_exists: 'replace', 'append' ou 'fail'
            batch_size: Taille des batchs pour insertion
        """
        if df.empty:
            logger.warning(f"DataFrame vide, aucune donnée chargée dans {table_name}")
            return 0

        full_table_name = f"{self.schema}.{table_name}"

        try:
            start_time = datetime.now()

            # Créer/recréer la table si nécessaire
            if if_exists == 'replace':
                self.create_table_from_dataframe(df, table_name, if_exists='replace')

            # Préparer les données
            df = df.copy()
            df = df.where(pd.notnull(df), None)  # Remplacer NaN par None

            # Colonnes à insérer
            columns = list(df.columns)
            columns_str = ', '.join([f'"{col}"' for col in columns])

            # Insertion par batch pour performance
            total_rows = len(df)
            inserted_rows = 0

            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i + batch_size]
                values = [tuple(row) for row in batch.values]

                # Construction de la requête avec placeholders
                placeholders = ','.join(['%s'] * len(columns))
                insert_query = f"""
                    INSERT INTO {full_table_name} ({columns_str})
                    VALUES ({placeholders})
                """

                extras.execute_batch(self.cursor, insert_query, values, page_size=batch_size)
                self.connection.commit()

                inserted_rows += len(batch)
                if inserted_rows % 5000 == 0:
                    logger.info(f"  {inserted_rows}/{total_rows} lignes insérées...")

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"✓ {inserted_rows} lignes chargées dans {full_table_name} ({duration:.2f}s)")

            return inserted_rows

        except Exception as e:
            self.connection.rollback()
            logger.error(f"Erreur chargement données dans {table_name}: {e}")
            raise

    def upsert_dataframe(self, df: pd.DataFrame, table_name: str,
                        conflict_columns: List[str], batch_size: int = 1000):
        """
        Upsert (INSERT ON CONFLICT UPDATE) d'un DataFrame

        Args:
            df: DataFrame à upserter
            table_name: Nom de la table
            conflict_columns: Colonnes pour détecter les conflits (clés)
            batch_size: Taille des batchs
        """
        if df.empty:
            logger.warning(f"DataFrame vide, aucun upsert dans {table_name}")
            return 0

        full_table_name = f"{self.schema}.{table_name}"

        try:
            df = df.copy()
            df = df.where(pd.notnull(df), None)

            columns = list(df.columns)
            columns_str = ', '.join([f'"{col}"' for col in columns])
            placeholders = ','.join(['%s'] * len(columns))

            # Clause UPDATE pour conflits
            update_cols = [col for col in columns if col not in conflict_columns]
            update_clause = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in update_cols])

            conflict_str = ', '.join([f'"{col}"' for col in conflict_columns])

            upsert_query = f"""
                INSERT INTO {full_table_name} ({columns_str})
                VALUES ({placeholders})
                ON CONFLICT ({conflict_str})
                DO UPDATE SET {update_clause}
            """

            total_rows = len(df)
            upserted_rows = 0

            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i + batch_size]
                values = [tuple(row) for row in batch.values]

                extras.execute_batch(self.cursor, upsert_query, values, page_size=batch_size)
                self.connection.commit()

                upserted_rows += len(batch)

            logger.info(f"✓ {upserted_rows} lignes upsertées dans {full_table_name}")
            return upserted_rows

        except Exception as e:
            self.connection.rollback()
            logger.error(f"Erreur upsert dans {table_name}: {e}")
            raise

    def get_last_sync_date(self, table_name: str) -> Optional[datetime]:
        """
        Récupère la date de dernière synchronisation d'une table

        Args:
            table_name: Nom de la table

        Returns:
            Date de dernière sync ou None
        """
        query = f"""
            SELECT last_sync_date
            FROM {self.schema}.sync_metadata
            WHERE table_name = %s
        """

        try:
            self.cursor.execute(query, (table_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except:
            return None

    def update_sync_metadata(self, table_name: str, record_count: int):
        """
        Met à jour les métadonnées de synchronisation

        Args:
            table_name: Nom de la table
            record_count: Nombre d'enregistrements
        """
        query = f"""
            INSERT INTO {self.schema}.sync_metadata (table_name, last_sync_date, total_records)
            VALUES (%s, NOW(), %s)
            ON CONFLICT (table_name)
            DO UPDATE SET last_sync_date = NOW(), total_records = %s
        """

        try:
            self.cursor.execute(query, (table_name, record_count, record_count))
            self.connection.commit()
        except Exception as e:
            logger.warning(f"Erreur mise à jour metadata: {e}")

    def log_etl_execution(self, table_name: str, records_extracted: int,
                         records_loaded: int, status: str,
                         error_message: str = None, execution_time: float = 0):
        """
        Log une exécution ETL

        Args:
            table_name: Nom de la table
            records_extracted: Nombre d'enregistrements extraits
            records_loaded: Nombre d'enregistrements chargés
            status: Statut (success, failed, partial)
            error_message: Message d'erreur si échec
            execution_time: Temps d'exécution en secondes
        """
        query = f"""
            INSERT INTO {self.schema}.etl_logs
            (table_name, records_extracted, records_loaded, status, error_message, execution_time_seconds)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            self.cursor.execute(query, (
                table_name, records_extracted, records_loaded,
                status, error_message, execution_time
            ))
            self.connection.commit()
        except Exception as e:
            logger.warning(f"Erreur log ETL: {e}")
