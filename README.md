# ETL Pennylane Open-Source

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![GitHub last commit](https://img.shields.io/github/last-commit/yves34690/Penny)](https://github.com/yves34690/Penny/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/yves34690/Penny)](https://github.com/yves34690/Penny/stargazers)

---

## En une phrase

**Synchronisez automatiquement vos donnees Pennylane vers PostgreSQL via l'API v2 avec sync incrementale, et connectez Power BI pour des analyses ultra-rapides.**

---

## Pourquoi ce projet ?

### Le probleme

Vous etes **expert-comptable**, **DAF** ou **data analyst** et vous rencontrez ces difficultes :

- **Actualisation Power BI = 30-60 minutes** a cause des transformations lourdes dans Power Query
- **Dependance au plan Premium Pennylane** pour acceder a Redshift (Data Sharing)
- **Full replace a chaque sync** = lent et inutile pour quelques lignes modifiees
- **Impossible de reutiliser** les donnees transformees ailleurs (Excel, Tableau, Python)

### La solution

Ce projet ETL open-source resout tous ces problemes :

- **Architecture 100% API REST v2** : plus aucune dependance a Redshift/Data Sharing
- **Sync incrementale** via changelogs Pennylane (quelques secondes au lieu de 8 minutes)
- **UPSERT intelligent** : seules les donnees modifiees sont mises a jour
- **Synchronisation automatique toutes les 2 heures** + full reload quotidien a 3h
- **13 tables** centralisees dans PostgreSQL, reutilisables partout

---

## Notre solution vs Power Query : Comparaison

| Critere | **ETL Python + PostgreSQL** | **Power Query Direct** |
|---------|-------------------------------|------------------------|
| **Temps actualisation** | **2-5 min** | 30-60 min |
| **Performance** | Tres rapide | Lent |
| **Gros volumes** | Millions de lignes | ~500k lignes max |
| **Reutilisabilite** | Excel, Tableau, Python | Uniquement Power BI |
| **Collaboration** | Base centralisee | Fichier .pbix par personne |
| **Dependance Redshift** | **Non** (100% API) | Oui (plan Premium) |
| **Sync incrementale** | **Oui** (changelogs) | Non |
| **Scalabilite** | Serveur | PC utilisateur |
| **Frequence actualisation** | Toutes les 2h automatique | Manuel ou 8x/jour max |

---

## Architecture

```
                         PENNYLANE API v2
                              |
              +---------------+---------------+
              |               |               |
         Changelogs      Endpoints       Exports POST
        (7 tables)      (4 tables)       (2 tables)
              |               |               |
              v               v               v
     +------------------------------------------+
     |        INCREMENTAL SYNC ENGINE           |
     |        (src/incremental_sync.py)         |
     |                                          |
     |  Changelog tables : UPSERT/DELETE        |
     |  Full replace tables : DROP + INSERT     |
     |  Export tables : POST + poll + download  |
     +------------------------------------------+
              |               |
              v               v
     +------------------+  +------------------+
     |   POSTGRESQL     |  |   SYNC STATE     |
     |   Schema:        |  |   (tracking)     |
     |   pennylane      |  |                  |
     |   13 tables      |  |  last_sync_at    |
     +--------+---------+  +------------------+
              |
     +--------+--------+
     |                  |
  POWER BI         JUPYTER / Excel
  Desktop          (usage manuel)
```

### Scheduler automatique

```
Sync incrementale : toutes les 2 heures (rapide, quelques secondes)
Full reload       : tous les jours a 03:00 (complet, garantit coherence)
```

Le full reload quotidien garantit la coherence meme si un changelog est rate (les changelogs ne remontent que 4 semaines max).

---

## Quick Start (5 minutes)

### Prerequis

- **Windows, Mac ou Linux**
- **Python 3.12+** installe
- **Docker Desktop** installe ([Guide installation](GUIDE_INSTALLATION_DOCKER.md))
- **Token API Pennylane** (Parametres > Connectivite > Developpeurs, avec tous les scopes)

### Installation

```bash
# 1. Cloner le projet
git clone https://github.com/yves34690/Penny.git
cd Penny

# 2. Configurer vos credentials
cp .env.example .env
# Editer .env : ajouter votre PENNYLANE_API_TOKEN et mot de passe PostgreSQL

# 3. Demarrer le systeme complet
docker-compose up -d

# 4. Verifier que tout est OK (optionnel)
python verify_setup.py
```

**C'est tout !** Le systeme est maintenant **100% automatique** :
- PostgreSQL demarre sur le port 5433
- Scheduler en cours d'execution
- Premier full import en cours (~8 min)
- Sync incrementale toutes les 2 heures

### Suivre les logs

```bash
docker-compose logs scheduler -f
```

### Connexion Power BI

```
Power BI Desktop > Obtenir les donnees > PostgreSQL
  Serveur : localhost:5433
  Base    : pennylane_db
  Schema  : pennylane
```

Guide complet : [GUIDE_POWERBI_CONNEXION.md](GUIDE_POWERBI_CONNEXION.md)

---

## Tables disponibles

### Tables avec sync incrementale (changelogs)

| Table | Endpoint API | Description |
|-------|-------------|-------------|
| **customers** | GET /customers | Clients |
| **suppliers** | GET /suppliers | Fournisseurs |
| **customer_invoices** | GET /customer_invoices | Factures clients |
| **supplier_invoices** | GET /supplier_invoices | Factures fournisseurs |
| **products** | GET /products | Produits/services |
| **transactions** | GET /transactions | Transactions bancaires |
| **ledger_entry_lines** | GET /ledger_entry_lines | Detail des ecritures comptables |

### Tables en full replace (pas de changelog)

| Table | Endpoint API | Description |
|-------|-------------|-------------|
| **ledger_entries** | GET /ledger_entries | Ecritures comptables (grand livre) |
| **ledger_accounts** | GET /ledger_accounts | Plan comptable |
| **bank_accounts** | GET /bank_accounts | Comptes bancaires |
| **fiscal_years** | GET /fiscal_years | Exercices fiscaux |

### Tables d'export

| Table | Endpoint API | Description |
|-------|-------------|-------------|
| **analytical_ledger** | POST /exports/analytical_general_ledger | Grand livre analytique |
| **fec** | POST /exports/fec | Fichier des Ecritures Comptables |

**Total : 13 tables** synchronisees automatiquement via API v2.

---

## Usage en ligne de commande

```bash
# Sync incrementale (defaut, rapide)
python src/incremental_sync.py

# Force full import de toutes les tables
python src/incremental_sync.py --full

# Sync une seule table
python src/incremental_sync.py --table customers
```

---

## Structure du projet

```
Penny/
|-- .env.example                         # Template credentials (a copier)
|-- .env                                 # VOS secrets (jamais commite)
|-- docker-compose.yml                   # PostgreSQL + pgAdmin + Scheduler
|-- Dockerfile                           # Image Docker du scheduler
|-- requirements.txt                     # Dependances Python
|
|-- src/
|   |-- incremental_sync.py             # Moteur de sync incrementale
|   |-- notebook_scheduler.py           # Scheduler (orchestre la sync)
|   |-- pennylane_api_client.py         # Client API Pennylane v2
|
|-- init_db/
|   |-- 001_sync_state.sql             # Table de suivi des syncs
|
|-- data/API Publique/
|   |-- Import_customers.ipynb          # Notebooks (usage manuel/debug)
|   |-- Import_analytical_ledger.ipynb
|   |-- ... (12 notebooks)
|
|-- logs/
|   |-- incremental_sync.log           # Logs de la sync
|   |-- notebook_scheduler.log         # Logs du scheduler
|
|-- GUIDE_INCREMENTAL_SYNC.md          # Guide deploiement incremental
|-- GUIDE_DEBUTANT.md                  # Demarrage sans code
|-- GUIDE_INSTALLATION_DOCKER.md       # Installer Docker
|-- GUIDE_POWERBI_CONNEXION.md         # Connecter Power BI
```

---

## Monitoring

### Table sync_state

```sql
SELECT table_name, last_sync_at, records_synced, sync_type, updated_at
FROM pennylane.sync_state
ORDER BY updated_at DESC;
```

### Logs Docker

```bash
# Etat des conteneurs
docker-compose ps

# Logs en temps reel
docker-compose logs scheduler -f

# Logs depuis le dernier demarrage
docker-compose logs scheduler --tail 100
```

### Sortie attendue

```
[START] Sync INCREMENTALE - 2026-02-20 14:00:00
[CHANGELOG] customer_invoices: 2 insert, 1 update, 0 delete
[UPSERT] customer_invoices: 3 enregistrements upsert
[SKIP] customers: aucun changement depuis 2026-02-20T12:00:00Z
...
[END] Sync terminee en 4.2s
[END] Succes: 13/13 | Erreurs: 0
```

---

## Gestion PostgreSQL

### Interface graphique pgAdmin

**URL** : [http://localhost:5050](http://localhost:5050)

**Credentials** (par defaut) :
- Email : `admin@pennylane.local`
- Password : `admin`

### Connexion serveur dans pgAdmin

1. Clic droit sur "Servers" > Register > Server
2. Onglet General : Name = `Pennylane Local`
3. Onglet Connection :
   - Host : `postgres` (nom du conteneur Docker)
   - Port : `5432` (port interne Docker)
   - Database : `pennylane_db`
   - Username : `pennylane_user`
   - Password : (voir `.env`)

---

## Depannage

### Erreur : "Token API invalide"

Regenerer le token dans Pennylane > Parametres > Connectivite > Developpeurs et mettre a jour `.env`.

### Erreur : "Cannot connect to PostgreSQL"

```bash
docker ps
# Doit afficher les conteneurs "Up"
docker-compose restart
```

### Rate limit atteint

Normal, le client attend automatiquement. `PENNYLANE_RATE_LIMIT=4.5` par defaut.

### Table vide apres sync

1. Verifier les logs : `docker-compose logs scheduler --tail 50`
2. Forcer un full import : `python src/incremental_sync.py --table <nom> --full`
3. Verifier que le token a les bons scopes

### Voir les logs

```bash
# Windows
type logs\incremental_sync.log

# Linux/Mac
cat logs/incremental_sync.log
```

---

## Securite des credentials

- **`.env.example`** : Template public (commite sur GitHub)
- **`.env`** : VOS secrets (ignore par Git, **jamais commite**)

### Variables obligatoires

```bash
# Token API Pennylane (seule source de donnees)
PENNYLANE_API_TOKEN=votre_token_api_rest

# PostgreSQL local (Docker)
POSTGRES_USER=pennylane_user
POSTGRES_PASSWORD=votre_mot_de_passe_securise
POSTGRES_DB=pennylane_db
```

---

## Contribution

Ce projet est **open-source** et concu pour etre **forkable** facilement.

1. **NE JAMAIS** commiter `.env` (vos secrets)
2. Mettre a jour `.env.example` si nouvelles variables
3. Documenter vos modifications

### Deploiement chez un client

```bash
git clone https://github.com/votre-username/Penny.git
cd Penny
cp .env.example .env
# Editer .env avec le token API du client
docker-compose up -d
```

Voir [GUIDE_INCREMENTAL_SYNC.md](GUIDE_INCREMENTAL_SYNC.md) pour le guide complet.

---

## Licence

**MIT License** - Libre d'utilisation, modification et redistribution.

Voir [LICENSE](LICENSE) pour details.

---

## Support

- **Documentation Pennylane API** : [pennylane.readme.io](https://pennylane.readme.io/)
- **Issues GitHub** : [github.com/yves34690/Penny/issues](https://github.com/yves34690/Penny/issues)

---

**Auteur** : Yves Cloarec
**Version** : 4.0 (Architecture 100% API v2 + Sync Incrementale)
**Date** : Fevrier 2026
