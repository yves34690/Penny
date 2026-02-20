"""
Sync incrementale Pennylane -> PostgreSQL via API v2

Modes:
    python src/incremental_sync.py              # sync incrementale (defaut)
    python src/incremental_sync.py --full       # force full import
    python src/incremental_sync.py --table customers  # sync une seule table

Architecture:
    - Tables avec changelog : sync incrementale (upsert/delete)
    - Tables sans changelog : full replace via API v2
    - Tables d'export : workflow POST + polling + download
"""

import os
import sys
import argparse
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Ajouter le repertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.pennylane_api_client import PennylaneClient

# ============================================================================
# CONFIGURATION
# ============================================================================

# Tables supportees par les changelogs (sync incrementale)
CHANGELOG_TABLES = {
    "customers": {
        "endpoint": "/customers",
        "changelog_resource": "customers",
    },
    "suppliers": {
        "endpoint": "/suppliers",
        "changelog_resource": "suppliers",
    },
    "customer_invoices": {
        "endpoint": "/customer_invoices",
        "changelog_resource": "customer_invoices",
    },
    "supplier_invoices": {
        "endpoint": "/supplier_invoices",
        "changelog_resource": "supplier_invoices",
    },
    "products": {
        "endpoint": "/products",
        "changelog_resource": "products",
    },
    "transactions": {
        "endpoint": "/transactions",
        "changelog_resource": "transactions",
    },
    "ledger_entry_lines": {
        "endpoint": "/ledger_entry_lines",
        "changelog_resource": "ledger_entry_lines",
        "extra_headers": {"X-Use-2026-API-Changes": "true"},
    },
}

# Tables sans changelog (full replace via API)
FULL_REPLACE_TABLES = {
    "ledger_entries": {
        "endpoint": "/ledger_entries",
        "extra_headers": {"X-Use-2026-API-Changes": "true"},
    },
    "ledger_accounts": {
        "endpoint": "/ledger_accounts",
        "extra_headers": {"X-Use-2026-API-Changes": "true"},
    },
    "bank_accounts": {
        "endpoint": "/bank_accounts",
    },
    "fiscal_years": {
        "endpoint": "/fiscal_years",
        "extra_headers": {"X-Use-2026-API-Changes": "true"},
    },
}

# Tables d'export (workflow POST specifique)
EXPORT_TABLES = {
    "analytical_ledger": {
        "export_method": "export_analytical_ledger",
    },
    "fec": {
        "export_method": "export_fec",
    },
}

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/incremental_sync.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONNEXION POSTGRESQL
# ============================================================================


def get_pg_connection():
    """Cree une connexion PostgreSQL depuis les variables d'environnement"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        database=os.getenv("POSTGRES_DB", "pennylane_db"),
        user=os.getenv("POSTGRES_USER", "pennylane_user"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def ensure_schema_and_sync_state(conn):
    """Cree le schema pennylane et la table sync_state si necessaire"""
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS pennylane")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pennylane.sync_state (
                table_name VARCHAR(100) PRIMARY KEY,
                last_sync_at TIMESTAMP NOT NULL DEFAULT NOW(),
                last_processed_at VARCHAR(255),
                records_synced INTEGER DEFAULT 0,
                sync_type VARCHAR(20) DEFAULT 'full',
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
    conn.commit()


def get_last_sync(conn, table_name: str) -> str | None:
    """Recupere la date de derniere sync pour une table"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT last_sync_at FROM pennylane.sync_state WHERE table_name = %s",
            (table_name,),
        )
        row = cur.fetchone()
        if row and row[0]:
            return row[0].strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def update_sync_state(conn, table_name: str, records_synced: int, sync_type: str):
    """Met a jour l'etat de sync pour une table"""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO pennylane.sync_state (table_name, last_sync_at, records_synced, sync_type, updated_at)
            VALUES (%s, NOW(), %s, %s, NOW())
            ON CONFLICT (table_name) DO UPDATE SET
                last_sync_at = NOW(),
                records_synced = EXCLUDED.records_synced,
                sync_type = EXCLUDED.sync_type,
                updated_at = NOW()
        """,
            (table_name, records_synced, sync_type),
        )
    conn.commit()


# ============================================================================
# OPERATIONS POSTGRESQL
# ============================================================================


def full_replace_table(conn, table_name: str, df: pd.DataFrame):
    """Remplace completement une table PostgreSQL avec un DataFrame"""
    if df.empty:
        logger.warning(f"[SKIP] {table_name}: DataFrame vide, table non modifiee")
        return 0

    schema = "pennylane"
    columns = list(df.columns)

    with conn.cursor() as cur:
        # Drop + recreate pour schema propre
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table_name} CASCADE")

        # Construire CREATE TABLE dynamique a partir du DataFrame
        col_defs = []
        for col in columns:
            dtype = df[col].dtype
            if dtype == "int64":
                pg_type = "BIGINT"
            elif dtype == "float64":
                pg_type = "DOUBLE PRECISION"
            elif dtype == "bool":
                pg_type = "BOOLEAN"
            else:
                pg_type = "TEXT"
            col_defs.append(f'"{col}" {pg_type}')

        create_sql = f"CREATE TABLE {schema}.{table_name} ({', '.join(col_defs)})"
        cur.execute(create_sql)

        # Ajouter PK sur id si la colonne existe
        if "id" in columns:
            cur.execute(f"ALTER TABLE {schema}.{table_name} ADD PRIMARY KEY (id)")

        # Insert en batch
        col_names = ", ".join(f'"{c}"' for c in columns)
        template = f"({', '.join(['%s'] * len(columns))})"

        # Convertir NaN en None pour PostgreSQL
        records = df.where(df.notna(), None).values.tolist()

        execute_values(
            cur,
            f"INSERT INTO {schema}.{table_name} ({col_names}) VALUES %s",
            records,
            template=template,
            page_size=500,
        )

    conn.commit()
    logger.info(f"[REPLACE] {table_name}: {len(df)} enregistrements charges")
    return len(df)


def upsert_records(conn, table_name: str, records: list[dict]):
    """UPSERT (INSERT ON CONFLICT DO UPDATE) pour des enregistrements"""
    if not records:
        return 0

    schema = "pennylane"
    df = pd.DataFrame(records)
    columns = list(df.columns)

    if "id" not in columns:
        logger.warning(f"[SKIP] {table_name}: pas de colonne 'id', upsert impossible")
        return 0

    with conn.cursor() as cur:
        # S'assurer que la table existe (si premiere sync incrementale)
        cur.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = '{schema}' AND table_name = '{table_name}'
            )
        """)
        table_exists = cur.fetchone()[0]

        if not table_exists:
            logger.info(
                f"[CREATE] Table {schema}.{table_name} n'existe pas, full replace"
            )
            conn.commit()
            return full_replace_table(conn, table_name, df)

        # Upsert
        col_names = ", ".join(f'"{c}"' for c in columns)
        template = f"({', '.join(['%s'] * len(columns))})"
        update_cols = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in columns if c != "id")

        records_list = df.where(df.notna(), None).values.tolist()

        sql = f"""
            INSERT INTO {schema}.{table_name} ({col_names}) VALUES %s
            ON CONFLICT (id) DO UPDATE SET {update_cols}
        """

        execute_values(cur, sql, records_list, template=template, page_size=500)

    conn.commit()
    logger.info(f"[UPSERT] {table_name}: {len(records)} enregistrements upsert")
    return len(records)


def delete_records(conn, table_name: str, ids: list[int]):
    """Supprime des enregistrements par ID"""
    if not ids:
        return 0

    schema = "pennylane"

    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {schema}.{table_name} WHERE id = ANY(%s)", (ids,))
        deleted = cur.rowcount

    conn.commit()
    logger.info(f"[DELETE] {table_name}: {deleted} enregistrements supprimes")
    return deleted


# ============================================================================
# LOGIQUE DE SYNC
# ============================================================================


def sync_changelog_table(
    client: PennylaneClient,
    conn,
    table_name: str,
    config: dict,
    force_full: bool = False,
):
    """Sync incrementale d'une table via changelog"""
    logger.info(f"{'='*60}")
    logger.info(f"[SYNC] {table_name} (changelog)")

    last_sync = None if force_full else get_last_sync(conn, table_name)

    # Full import si jamais sync ou force
    if not last_sync:
        logger.info(f"[FULL] {table_name}: premier import ou force full")
        extra_headers = config.get("extra_headers")
        data = client.fetch_all_raw(config["endpoint"], extra_headers=extra_headers)
        df = pd.DataFrame(data) if data else pd.DataFrame()
        count = full_replace_table(conn, table_name, df)
        update_sync_state(conn, table_name, count, "full")
        return

    # Sync incrementale via changelog
    changes = client.get_changelog(config["changelog_resource"], last_sync)

    if not changes:
        logger.info(f"[SKIP] {table_name}: aucun changement depuis {last_sync}")
        update_sync_state(conn, table_name, 0, "incremental")
        return

    # Trier les changements par operation
    inserts = [c["id"] for c in changes if c.get("operation") in ("insert", "create")]
    updates = [c["id"] for c in changes if c.get("operation") == "update"]
    deletes = [c["id"] for c in changes if c.get("operation") == "delete"]

    logger.info(
        f"[CHANGELOG] {table_name}: {len(inserts)} insert, {len(updates)} update, {len(deletes)} delete"
    )

    total = 0

    # Fetch et upsert pour insert + update
    upsert_ids = list(set(inserts + updates))
    if upsert_ids:
        extra_headers = config.get("extra_headers")
        records = client.get_by_ids(
            config["endpoint"], upsert_ids, extra_headers=extra_headers
        )
        total += upsert_records(conn, table_name, records)

    # Delete
    if deletes:
        total += delete_records(conn, table_name, deletes)

    update_sync_state(conn, table_name, total, "incremental")


def sync_full_replace_table(
    client: PennylaneClient, conn, table_name: str, config: dict
):
    """Full replace d'une table via API v2 (pas de changelog disponible)"""
    logger.info(f"{'='*60}")
    logger.info(f"[SYNC] {table_name} (full replace API)")

    extra_headers = config.get("extra_headers")
    data = client.fetch_all_raw(config["endpoint"], extra_headers=extra_headers)
    df = pd.DataFrame(data) if data else pd.DataFrame()
    count = full_replace_table(conn, table_name, df)
    update_sync_state(conn, table_name, count, "full")


def sync_export_table(client: PennylaneClient, conn, table_name: str, config: dict):
    """Sync d'une table via export POST (FEC, Grand Livre Analytique)"""
    logger.info(f"{'='*60}")
    logger.info(f"[SYNC] {table_name} (export)")

    try:
        export_method = getattr(client, config["export_method"])
        result = export_method()

        download_url = result.get("download_url") or result.get("url")
        if not download_url:
            logger.warning(
                f"[SKIP] {table_name}: pas d'URL de telechargement dans la reponse"
            )
            logger.warning(f"  Reponse: {result}")
            return

        df = client.download_export(download_url)
        count = full_replace_table(conn, table_name, df)
        update_sync_state(conn, table_name, count, "export")

    except Exception as e:
        logger.error(f"[ERREUR] {table_name}: {e}")


# ============================================================================
# MAIN
# ============================================================================


def run_sync(force_full: bool = False, table_filter: str = None):
    """Execute la synchronisation"""
    start_time = time.time()

    logger.info("=" * 80)
    logger.info(
        f"[START] Sync {'FULL' if force_full else 'INCREMENTALE'} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    if table_filter:
        logger.info(f"[FILTER] Table unique: {table_filter}")
    logger.info("=" * 80)

    # Charger .env
    load_dotenv()

    # Init client API
    client = PennylaneClient(env_path=".env")

    # Connexion PostgreSQL
    conn = get_pg_connection()
    ensure_schema_and_sync_state(conn)

    success_count = 0
    error_count = 0

    def should_sync(name):
        return table_filter is None or table_filter == name

    # 1. Tables avec changelog
    for table_name, config in CHANGELOG_TABLES.items():
        if not should_sync(table_name):
            continue
        try:
            sync_changelog_table(client, conn, table_name, config, force_full)
            success_count += 1
        except Exception as e:
            logger.error(f"[ERREUR] {table_name}: {e}")
            error_count += 1

    # 2. Tables full replace
    for table_name, config in FULL_REPLACE_TABLES.items():
        if not should_sync(table_name):
            continue
        try:
            sync_full_replace_table(client, conn, table_name, config)
            success_count += 1
        except Exception as e:
            logger.error(f"[ERREUR] {table_name}: {e}")
            error_count += 1

    # 3. Tables d'export
    for table_name, config in EXPORT_TABLES.items():
        if not should_sync(table_name):
            continue
        try:
            sync_export_table(client, conn, table_name, config)
            success_count += 1
        except Exception as e:
            logger.error(f"[ERREUR] {table_name}: {e}")
            error_count += 1

    conn.close()

    duration = time.time() - start_time
    total = success_count + error_count

    logger.info("=" * 80)
    logger.info(f"[END] Sync terminee en {duration:.1f}s")
    logger.info(f"[END] Succes: {success_count}/{total} | Erreurs: {error_count}")
    logger.info("=" * 80)

    return error_count == 0


def main():
    parser = argparse.ArgumentParser(
        description="Sync incrementale Pennylane -> PostgreSQL"
    )
    parser.add_argument(
        "--full", action="store_true", help="Force full import de toutes les tables"
    )
    parser.add_argument(
        "--table", type=str, help="Sync une seule table (ex: customers)"
    )
    args = parser.parse_args()

    # Verifier que la table demandee existe
    if args.table:
        all_tables = (
            set(CHANGELOG_TABLES) | set(FULL_REPLACE_TABLES) | set(EXPORT_TABLES)
        )
        if args.table not in all_tables:
            print(f"[ERREUR] Table '{args.table}' inconnue. Tables disponibles:")
            for t in sorted(all_tables):
                print(f"  - {t}")
            sys.exit(1)

    success = run_sync(force_full=args.full, table_filter=args.table)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
