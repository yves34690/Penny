# Afficher la liste des tables disponibles via Redshift Pennylane

import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv(dotenv_path='../.env')

# Connexion Redshift Pennylane
conn = psycopg2.connect(
    host='pennylane-external.csqwamh5pldr.eu-west-1.redshift.amazonaws.com',
    port=5439,
    dbname='prod',
    user='u_289572',
    password=os.getenv('PENNYLANE_DATA_SHARING_KEY')
)

print("Connexion Redshift etablie")

# Requête pour lister TOUTES les tables disponibles
query_tables = """
    SELECT
        schemaname as schema,
        tablename as table,
        'table' as type
    FROM pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_internal')

    UNION ALL

    SELECT
        schemaname as schema,
        viewname as table,
        'view' as type
    FROM pg_views
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_internal')

    ORDER BY schema, table;
"""

# Exécuter la requête
df_tables = pd.read_sql(query_tables, conn)

# Afficher le résultat
print(f"\n{len(df_tables)} tables/views disponibles dans Redshift Pennylane:\n")
print(df_tables.to_string(index=False))

# Afficher par schéma pour plus de clarté
print("\n" + "="*80)
print("RESUME PAR SCHEMA:")
print("="*80)

for schema in df_tables['schema'].unique():
    tables_in_schema = df_tables[df_tables['schema'] == schema]
    print(f"\nSchema: {schema} ({len(tables_in_schema)} tables/views)")
    for idx, row in tables_in_schema.iterrows():
        print(f"  [{row['type']}] {row['table']}")

# Fermer la connexion
conn.close()
print("\nConnexion fermee")
