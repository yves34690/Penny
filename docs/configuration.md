# Configuration

## Variables d'environnement (.env)

Toutes les configurations sensibles sont stockées dans le fichier `.env`.

### Variables obligatoires

| Variable | Description | Exemple |
|----------|-------------|---------|
| `PENNYLANE_API_KEY` | Clé API Pennylane | `pl_live_abc123...` |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | `MonMotDePasse2025!` |

### Variables optionnelles

#### API Pennylane

```env
PENNYLANE_BASE_URL=https://app.pennylane.com/api/external/v1
PENNYLANE_RATE_LIMIT=4.5
```

#### PostgreSQL

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pennylane_data
POSTGRES_USER=pennylane_user
POSTGRES_SCHEMA=pennylane
```

#### Planificateur

```env
SCHEDULER_INTERVAL_MINUTES=10
SCHEDULER_ENABLED=true
```

#### Logging

```env
LOG_LEVEL=INFO
LOG_FILE=logs/pennylane_etl.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

## Configuration des endpoints (config.json)

Le fichier `config.json` définit quels endpoints Pennylane synchroniser.

### Structure

```json
{
  "endpoints": {
    "enabled": [
      {
        "name": "invoices",
        "endpoint": "/customer_invoices",
        "table_name": "invoices",
        "incremental": true,
        "date_field": "updated_at"
      }
    ]
  }
}
```

### Paramètres

- **name** : Nom descriptif
- **endpoint** : Chemin API Pennylane
- **table_name** : Nom table PostgreSQL
- **incremental** : Extraction incrémentielle (true/false)
- **date_field** : Champ date pour filtre incrémentiel

### Endpoints disponibles

| Endpoint | Description | Incrémentiel |
|----------|-------------|--------------|
| `/customer_invoices` | Factures clients | ✅ |
| `/supplier_invoices` | Factures fournisseurs | ✅ |
| `/customers` | Clients | ✅ |
| `/suppliers` | Fournisseurs | ✅ |
| `/transactions` | Transactions bancaires | ✅ |
| `/journal_entries` | Écritures comptables | ✅ |
| `/plan_items` | Plan comptable | ❌ |
| `/categories` | Catégories analytiques | ❌ |
| `/payment_methods` | Moyens de paiement | ❌ |

### Ajouter un endpoint

```json
{
  "name": "products",
  "endpoint": "/products",
  "table_name": "products",
  "incremental": true,
  "date_field": "updated_at"
}
```

## Configuration Docker

Le fichier `docker-compose.yml` utilise les variables `.env`.

### Ports par défaut

- PostgreSQL : `5432`
- pgAdmin : `5050`

### Changer les ports

Dans `.env` :

```env
POSTGRES_PORT=5433
PGADMIN_PORT=5051
```

## Sécurité

!!! danger "Ne JAMAIS commiter .env"
    Le fichier `.env` contient vos secrets et est ignoré par Git.

!!! tip "Bonnes pratiques"
    - Mot de passe PostgreSQL : 16+ caractères, majuscules, minuscules, chiffres, symboles
    - Clé API : Ne jamais partager, régénérer si compromise
    - Sauvegarder `.env` de façon sécurisée (gestionnaire mots de passe)
