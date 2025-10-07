# ETL Pennylane → PostgreSQL → Power BI

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-16-blue.svg)

Solution complète pour extraire les données Pennylane, les stocker dans PostgreSQL et les connecter à Power BI avec actualisation toutes les 10 minutes.

## 🎯 Objectifs

1. **Contourner la limite d'actualisation API Pennylane** (2h → 10 min)
2. **Accélérer l'actualisation Power BI** en externalisant les transformations
3. **Architecture scalable** pour gros volumes (millions de lignes)
4. **Module réutilisable** : Partagez facilement via GitHub

---

## 📁 Structure du projet

```
Penny/
├── .env.example                # Template variables d'environnement
├── .env                        # VOS secrets (jamais commité)
├── docker-compose.yml          # Configuration PostgreSQL
├── config.json                 # Configuration endpoints
├── requirements.txt            # Dépendances Python
├── src/
│   ├── config_loader.py       # Gestion .env et configuration
│   ├── pennylane_api.py       # Client API avec rate limiting
│   ├── database.py            # Gestion PostgreSQL
│   ├── transformations.py     # Transformations basiques
│   ├── main.py                # Script ETL principal
│   └── scheduler.py           # Planificateur automatique
├── init_db/
│   └── 01_init_schema.sql     # Initialisation base de données
├── logs/                       # Logs d'exécution
└── data/                       # Données temporaires (optionnel)
```

---

## 🚀 Installation rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-username/pennylane-etl.git
cd pennylane-etl
```

### 2. Créer votre fichier .env

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos vraies valeurs
notepad .env  # Windows
# ou
nano .env     # Linux/Mac
```

**Variables OBLIGATOIRES à configurer dans `.env` :**

```bash
PENNYLANE_API_KEY=votre_vraie_cle_api_pennylane
POSTGRES_PASSWORD=votre_mot_de_passe_securise
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 4. Démarrer PostgreSQL

```bash
docker-compose up -d
```

Vérifier :

```bash
docker ps
```

### 5. Lancer première extraction

```bash
cd src
python main.py full
```

✅ **Vous êtes prêt !**

---

## 🔐 Gestion des secrets

### Architecture de sécurité

- **`.env.example`** : Template public (committé sur GitHub)
- **`.env`** : VOS secrets (ignoré par Git, jamais committé)
- **`config.json`** : Configuration publique (endpoints, paramètres)

### Variables d'environnement (.env)

| Variable | Description | Requis |
|----------|-------------|--------|
| `PENNYLANE_API_KEY` | Clé API Pennylane | ✅ OUI |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | ✅ OUI |
| `POSTGRES_HOST` | Host PostgreSQL | Non (défaut: localhost) |
| `POSTGRES_PORT` | Port PostgreSQL | Non (défaut: 5432) |
| `SCHEDULER_INTERVAL_MINUTES` | Intervalle actualisation | Non (défaut: 10) |
| `LOG_LEVEL` | Niveau de log | Non (défaut: INFO) |

**Voir [.env.example](.env.example) pour la liste complète.**

---

## 📊 Utilisation

### Mode 1 : Extraction manuelle

#### Extraction complète (première fois)

```bash
cd src
python main.py full
```

#### Extraction incrémentielle (uniquement nouvelles données)

```bash
python main.py incremental
```

### Mode 2 : Planificateur automatique (10 min)

```bash
cd src
python scheduler.py
```

**Arrêter** : `Ctrl+C`

---

## 🔧 Gestion de PostgreSQL

### Interface graphique pgAdmin

[http://localhost:5050](http://localhost:5050)

Identifiants par défaut (modifiables dans `.env`) :
- Email : `admin@pennylane.local`
- Password : `admin`

### Connexion au serveur PostgreSQL

- **Host** : `localhost`
- **Port** : `5432`
- **Database** : `pennylane_data`
- **Username** : `pennylane_user`
- **Password** : voir `.env`

### Requêtes SQL utiles

```sql
-- Lister les tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'pennylane';

-- Logs ETL
SELECT * FROM pennylane.etl_logs
ORDER BY execution_date DESC LIMIT 10;

-- Métadonnées synchro
SELECT * FROM pennylane.sync_metadata;
```

---

## 📈 Connexion à Power BI

### Étape 1 : Connexion PostgreSQL

Power BI Desktop → **Obtenir les données** → **PostgreSQL**

```
Serveur : localhost
Base de données : pennylane_data
Mode : Importer
```

### Étape 2 : Sélectionner tables

Schéma `pennylane` → Sélectionner tables

### Étape 3 : Transformations dans Jupyter (recommandé)

```python
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Charger .env
load_dotenv()

# Connexion PostgreSQL
conn_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(conn_string)

# Charger données brutes
df = pd.read_sql('SELECT * FROM pennylane.invoices', engine)

# VOS TRANSFORMATIONS
df['montant_ht_euros'] = df['amount_cents'] / 100

# Sauvegarder dans table transformée
df.to_sql('invoices_transformed', engine, schema='pennylane', if_exists='replace', index=False)
```

Puis Power BI se connecte à `pennylane.invoices_transformed` !

---

## 🔍 Endpoints Pennylane

Configurés par défaut dans [config.json](config.json) :

| Endpoint | Table | Incrémentiel |
|----------|-------|--------------|
| `/customer_invoices` | invoices | ✅ |
| `/suppliers` | suppliers | ✅ |
| `/customers` | customers | ✅ |
| `/transactions` | transactions | ✅ |
| `/journal_entries` | journal_entries | ✅ |
| `/plan_items` | accounts | ❌ |
| `/categories` | categories | ❌ |
| `/payment_methods` | payment_methods | ❌ |

**Ajouter/modifier** : Éditer `config.json` section `endpoints.enabled`

---

## 🐛 Dépannage

### Erreur : "Variable d'environnement PENNYLANE_API_KEY requise"

→ Créer fichier `.env` depuis `.env.example` et configurer

### Erreur connexion PostgreSQL

```bash
docker ps  # Vérifier que postgres tourne
docker-compose restart postgres
```

### Erreur API 401 Unauthorized

→ Vérifier `PENNYLANE_API_KEY` dans `.env`

### Voir les logs

```bash
type logs\pennylane_etl.log  # Windows
cat logs/pennylane_etl.log   # Linux/Mac
```

---

## 📊 Architecture complète

```
┌─────────────┐
│  Pennylane  │  API (5 req/sec)
└──────┬──────┘
       │ Toutes les 10 min
       ▼
┌──────────────┐
│ Python ETL   │  Rate limiting + Extraction
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│          PostgreSQL (Docker)         │
│  ┌────────────┐    ┌──────────────┐ │
│  │  Tables    │ -> │   Tables     │ │
│  │  brutes    │    │ transformées │ │
│  └────────────┘    └──────────────┘ │
└───────┬──────────────────┬───────────┘
        │                  │
        ▼                  ▼
┌──────────────┐    ┌──────────────┐
│   Jupyter    │    │   Power BI   │
│Transformations│    │   Desktop    │
└──────────────┘    └──────────────┘
```

---

## 🎯 Gains attendus

| Aspect | Avant | Après |
|--------|-------|-------|
| **Actualisation Pennylane** | 2 heures | 10 minutes |
| **Actualisation Power BI** | 30-60 min | 2-5 min |
| **Transformations** | Power Query (lent) | Python/SQL (rapide) |
| **Volume supporté** | Limité | Millions de lignes |

---

## 🤝 Contribution

Ce projet est open-source et conçu pour être réutilisable.

### Partager votre configuration

1. **NE JAMAIS** commiter `.env`
2. Mettre à jour `.env.example` si nouvelles variables
3. Documenter dans README

### Déploiement chez un client

```bash
# 1. Cloner
git clone https://github.com/votre-username/pennylane-etl.git

# 2. Créer .env depuis template
cp .env.example .env

# 3. Configurer secrets du client
nano .env

# 4. Démarrer
docker-compose up -d
cd src && python main.py full
```

---

## 📝 Licence

MIT License - Libre d'utilisation et modification

---

## 📞 Support

- **Documentation Pennylane API** : [pennylane.readme.io](https://pennylane.readme.io/)
- **Issues GitHub** : [github.com/votre-username/pennylane-etl/issues](https://github.com/votre-username/pennylane-etl/issues)

---

**Auteur** : Généré avec Claude Code
**Version** : 2.0 (avec gestion .env)
**Date** : 2025
