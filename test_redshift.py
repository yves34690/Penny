"""
Script de test pour connexion Redshift Pennylane
"""

import psycopg2
import os
from dotenv import load_dotenv

# Charger .env
load_dotenv()

print("="*80)
print("TEST CONNEXION REDSHIFT PENNYLANE")
print("="*80)

# Recuperer credentials depuis .env
host = 'pennylane-external.csqwamh5pldr.eu-west-1.redshift.amazonaws.com'
port = 5439
dbname = 'prod'
user = 'u_289572'
password = os.getenv('PENNYLANE_DATA_SHARING_KEY')

print(f"\nHost: {host}")
print(f"Port: {port}")
print(f"Database: {dbname}")
print(f"User: {user}")
print(f"Password: {'*' * (len(password) if password else 0)}")

# Test de connexion
try:
    print("\nTentative de connexion...")

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=10
    )

    print("[OK] CONNEXION REUSSIE !")

    # Test requete simple
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\nVersion Redshift: {version[0][:80]}...")

    # Lister les schemas disponibles
    cursor.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
        ORDER BY schema_name;
    """)
    schemas = cursor.fetchall()

    if schemas:
        print(f"\nSchemas disponibles ({len(schemas)}):")
        for schema in schemas[:10]:
            print(f"   - {schema[0]}")
        if len(schemas) > 10:
            print(f"   ... et {len(schemas) - 10} autres")

    # Lister quelques tables
    cursor.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name
        LIMIT 20;
    """)
    tables = cursor.fetchall()

    if tables:
        print(f"\nExemples de tables ({len(tables)} affichees):")
        current_schema = None
        for schema, table in tables:
            if schema != current_schema:
                print(f"\n   Schema: {schema}")
                current_schema = schema
            print(f"      - {table}")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("[OK] ACCES REDSHIFT OPERATIONNEL !")
    print("="*80)
    print("\nVous pouvez utiliser cette connexion dans vos Jupyter Notebooks.")

except psycopg2.OperationalError as e:
    print("\n[ERREUR] CONNEXION IMPOSSIBLE")
    print(f"\nDetails: {str(e)}")
    print("\nCauses possibles:")
    print("   1. Credentials incorrects (verifier Data Sharing Key)")
    print("   2. Acces Redshift non active pour votre compte")
    print("   3. Probleme reseau / Firewall")
    print("   4. IP non autorisee (si whitelist activee)")

except Exception as e:
    print(f"\n[ERREUR] INATTENDUE: {type(e).__name__}")
    print(f"Details: {str(e)}")

print("\n")
