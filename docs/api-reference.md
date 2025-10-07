# API Reference

Documentation des modules Python de Penny.

## config_loader

Module de chargement de configuration depuis `.env` et `config.json`.

### `load_full_config()`

Charge la configuration complète.

```python
from config_loader import load_full_config

config = load_full_config()
```

**Returns:** `Dict[str, Any]` - Configuration complète

**Raises:** `ValueError` si configuration invalide

### `get_env(key, default, required)`

Récupère une variable d'environnement.

```python
from config_loader import get_env

api_key = get_env('PENNYLANE_API_KEY', required=True)
```

**Parameters:**
- `key` (str): Nom de la variable
- `default` (Any): Valeur par défaut
- `required` (bool): Si True, erreur si absent

**Returns:** Valeur de la variable

## pennylane_api

Client API Pennylane avec rate limiting.

### `PennylaneAPI`

Client pour l'API Pennylane.

```python
from pennylane_api import PennylaneAPI

api = PennylaneAPI(
    api_key="votre_cle",
    base_url="https://app.pennylane.com/api/external/v1",
    rate_limit=4.5
)
```

#### Méthodes

##### `get_paginated_data(endpoint, params, max_pages)`

Récupère toutes les données paginées.

```python
data = api.get_paginated_data('/customer_invoices')
```

**Parameters:**
- `endpoint` (str): Endpoint API
- `params` (Dict, optional): Paramètres supplémentaires
- `max_pages` (int, optional): Limite de pages

**Returns:** `List[Dict]` - Tous les enregistrements

##### `get_incremental_data(endpoint, last_sync_date, date_field)`

Extraction incrémentielle.

```python
from datetime import datetime

last_sync = datetime(2025, 1, 1)
data = api.get_incremental_data(
    '/customer_invoices',
    last_sync,
    'updated_at'
)
```

**Returns:** `List[Dict]` - Enregistrements modifiés

##### `test_connection()`

Teste la connexion API.

```python
if api.test_connection():
    print("Connexion OK")
```

**Returns:** `bool`

## database

Gestion base de données PostgreSQL.

### `PostgresDatabase`

Gestionnaire PostgreSQL avec context manager.

```python
from database import PostgresDatabase

config = load_full_config()

with PostgresDatabase(config) as db:
    db.load_dataframe(df, 'table_name')
```

#### Méthodes

##### `load_dataframe(df, table_name, if_exists, batch_size)`

Charge un DataFrame dans PostgreSQL.

```python
rows = db.load_dataframe(
    df,
    'invoices',
    if_exists='replace',
    batch_size=1000
)
```

**Parameters:**
- `df` (pd.DataFrame): DataFrame à charger
- `table_name` (str): Nom de la table
- `if_exists` (str): 'replace', 'append', 'fail'
- `batch_size` (int): Taille des batchs

**Returns:** `int` - Nombre de lignes insérées

##### `upsert_dataframe(df, table_name, conflict_columns)`

Upsert (INSERT ON CONFLICT UPDATE).

```python
db.upsert_dataframe(
    df,
    'invoices',
    conflict_columns=['id']
)
```

##### `get_last_sync_date(table_name)`

Date de dernière synchronisation.

```python
last_sync = db.get_last_sync_date('invoices')
```

**Returns:** `datetime` ou `None`

## transformations

Transformations basiques des données.

### `DataTransformer`

Applique transformations minimales.

```python
from transformations import DataTransformer

transformer = DataTransformer(config)
df_clean = transformer.basic_transform(df, 'invoices')
```

#### Méthodes

##### `basic_transform(df, table_name)`

Nettoyage basique.

```python
df_clean = transformer.basic_transform(df, 'invoices')
```

**Transformations appliquées:**
- Normalisation noms colonnes (snake_case)
- Suppression doublons

##### `normalize_column_names(df)`

Normalise noms de colonnes (statique).

```python
df = DataTransformer.normalize_column_names(df)
```

## main

Script ETL principal.

### `main(mode)`

Exécution ETL.

```python
from main import main

main(mode='full')      # Extraction complète
main(mode='incremental')  # Incrémentiel
```

**Parameters:**
- `mode` (str): 'full' ou 'incremental'

## scheduler

Planificateur automatique.

### `ETLScheduler`

Planificateur pour exécutions répétées.

```python
from scheduler import ETLScheduler

scheduler = ETLScheduler(interval_minutes=10)
scheduler.start()
```

#### Méthodes

##### `start()`

Démarre le planificateur.

##### `stop()`

Arrête le planificateur.

## Exemples complets

### Extraction complète

```python
from config_loader import load_full_config
from pennylane_api import PennylaneAPI
from database import PostgresDatabase
import pandas as pd

# Configuration
config = load_full_config()

# API
api = PennylaneAPI(
    api_key=config['pennylane_api']['api_key'],
    base_url=config['pennylane_api']['base_url']
)

# Extraction
data = api.get_paginated_data('/customer_invoices')
df = pd.DataFrame(data)

# Chargement
with PostgresDatabase(config) as db:
    db.load_dataframe(df, 'invoices', if_exists='replace')
```

### Extraction incrémentielle

```python
from datetime import datetime

# Récupérer dernière sync
with PostgresDatabase(config) as db:
    last_sync = db.get_last_sync_date('invoices')

    # Extraction incrémentielle
    data = api.get_incremental_data(
        '/customer_invoices',
        last_sync,
        'updated_at'
    )

    if data:
        df = pd.DataFrame(data)
        db.load_dataframe(df, 'invoices', if_exists='append')
```
