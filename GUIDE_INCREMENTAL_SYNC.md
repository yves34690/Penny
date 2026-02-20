# Guide : Sync Incrementale Pennylane -> PostgreSQL

Architecture 100% API REST v2 avec synchronisation incrementale via changelogs.

---

## 1. Prerequis

### Token API Pennylane
1. Se connecter a Pennylane : https://app.pennylane.com
2. Aller dans **Parametres > Connectivite > Developpeurs**
3. Generer un token API avec **tous les scopes** :
   - customers, suppliers
   - customer_invoices, supplier_invoices
   - products, transactions
   - ledger_entries, ledger_accounts, ledger_entry_lines
   - bank_accounts, fiscal_years
   - exports (fec, analytical_general_ledger)
   - changelogs

### Infrastructure
- Docker + Docker Compose
- Port 5433 disponible (PostgreSQL)
- Port 5050 disponible (pgAdmin, optionnel)
- Connexion internet (API Pennylane)

---

## 2. Installation

```bash
# Cloner le depot
git clone <url-du-depot> Penny
cd Penny

# Configurer les variables d'environnement
copy .env.example .env
# Editer .env avec votre token API et mot de passe PostgreSQL

# Lancer l'infrastructure
docker-compose up -d
```

Au premier demarrage, le scheduler execute automatiquement un **full import** de toutes les tables.

---

## 3. Architecture 100% API

**Plus aucune dependance a Redshift/Data Sharing.**

Toutes les donnees sont recuperees via l'API REST v2 de Pennylane :

| Table | Source | Mode sync |
|---|---|---|
| customers | GET /customers | Incremental (changelog) |
| suppliers | GET /suppliers | Incremental (changelog) |
| customer_invoices | GET /customer_invoices | Incremental (changelog) |
| supplier_invoices | GET /supplier_invoices | Incremental (changelog) |
| products | GET /products | Incremental (changelog) |
| transactions | GET /transactions | Incremental (changelog) |
| ledger_entry_lines | GET /ledger_entry_lines | Incremental (changelog) |
| ledger_entries | GET /ledger_entries | Full replace |
| ledger_accounts | GET /ledger_accounts | Full replace |
| bank_accounts | GET /bank_accounts | Full replace |
| fiscal_years | GET /fiscal_years | Full replace |
| analytical_ledger | POST /exports/analytical_general_ledger | Export |
| fec | POST /exports/fec | Export |

---

## 4. Comment ca marche

### Sync incrementale (toutes les 2h)

Pour les tables supportees par les changelogs :

1. Lire `last_sync_at` depuis `pennylane.sync_state`
2. Appeler `GET /changelogs/{resource}?start_date=last_sync_at`
3. Collecter les IDs par operation (insert/update/delete)
4. Fetch les enregistrements complets pour insert/update
5. **UPSERT** dans PostgreSQL (`INSERT ON CONFLICT DO UPDATE`)
6. **DELETE** pour les suppressions
7. Mettre a jour `sync_state`

Pour les tables sans changelog : full replace a chaque cycle.

### Full reload (1x/jour a 03:00)

Toutes les tables sont reimportees completement. Garantit la coherence meme si un changelog a ete rate.

### Scheduler

```
Sync incrementale : toutes les 2 heures (rapide, quelques secondes)
Full reload       : tous les jours a 03:00 (complet, ~8 minutes)
```

---

## 5. Usage en ligne de commande

```bash
# Sync incrementale (defaut)
python src/incremental_sync.py

# Force full import
python src/incremental_sync.py --full

# Sync une seule table
python src/incremental_sync.py --table customers
python src/incremental_sync.py --table customer_invoices --full
```

---

## 6. Monitoring

### Table sync_state

```sql
SELECT table_name, last_sync_at, records_synced, sync_type, updated_at
FROM pennylane.sync_state
ORDER BY updated_at DESC;
```

### Logs

- Fichier : `logs/incremental_sync.log`
- Fichier scheduler : `logs/notebook_scheduler.log`
- Docker : `docker logs pennylane_scheduler`

---

## 7. Connexion Power BI

Inchangee : PostgreSQL sur `localhost:5433`, schema `pennylane`.

```
Serveur : localhost:5433
Base    : pennylane_db
Schema  : pennylane
User    : pennylane_user
```

---

## 8. Troubleshooting

### Token invalide
```
[ERREUR] Token API invalide - Verifiez PENNYLANE_API_TOKEN dans .env
```
-> Regenerer le token dans Pennylane > Parametres > Connectivite > Developpeurs

### Rate limit
```
[WARNING] Rate limit atteint, attente 60s...
```
-> Normal, le client attend automatiquement. PENNYLANE_RATE_LIMIT=4.5 par defaut.

### Table vide apres sync
1. Verifier les logs pour des erreurs
2. Lancer un full import : `python src/incremental_sync.py --table <nom> --full`
3. Verifier que le token a les bons scopes

### Changelog vide alors que des donnees ont change
Les changelogs ne sont disponibles que pour certaines ressources.
-> Les tables `ledger_entries`, `ledger_accounts`, `bank_accounts`, `fiscal_years` sont en mode full replace.

---

## 9. Limites

- **Changelogs = 4 semaines max** : au-dela, les changements ne sont plus disponibles.
  Le full reload quotidien a 03:00 compense cette limite.
- **Rate limit API** : 4.5 requetes/seconde. Le client gere automatiquement.
- **Exports FEC/analytique** : asynchrones, peuvent prendre quelques minutes.

---

*Derniere mise a jour : 2026-02-20*
