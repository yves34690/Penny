# 📖 Guide Utilisateur - ETL Pennylane

> **Version :** 1.0
> **Dernière mise à jour :** 2025-10-07
> **Auteur :** yves34690

---

## 📋 Table des matières

1. [Introduction](#introduction)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Utilisation quotidienne](#utilisation-quotidienne)
6. [Maintenance](#maintenance)
7. [Dépannage](#dépannage)
8. [Évolutions futures](#évolutions-futures)

---

## 🎯 Introduction

### Qu'est-ce que Penny ?

**Penny** est une solution ETL (Extract, Transform, Load) qui :
- Extrait les données de l'API Pennylane toutes les **10 minutes**
- Les stocke dans une base PostgreSQL
- Permet une connexion rapide à Power BI pour analyse

### Problèmes résolus

| Problème | Avant | Avec Penny |
|----------|-------|------------|
| Actualisation API Pennylane | 2 heures | 10 minutes |
| Actualisation Power BI | 30-60 min (lent) | 2-5 min (rapide) |
| Transformations données | Power Query | Python + SQL |
| Volume supporté | Limité | Millions de lignes |

### Architecture globale

```
Pennylane API → Python ETL (10 min) → PostgreSQL → Jupyter/Power BI
```

---

## 🔧 Prérequis

### Logiciels nécessaires

- [x] **Python 3.12+** ([télécharger](https://www.python.org/downloads/))
- [x] **Docker Desktop** ([télécharger](https://www.docker.com/products/docker-desktop/))
- [x] **Git** ([télécharger](https://git-scm.com/downloads))
- [x] **Éditeur de texte** (VS Code recommandé)

### Comptes et accès

- [x] **Compte Pennylane** avec offre Premium + Module comptable
- [x] **Clé API Pennylane** (voir [obtenir clé API](#obtenir-clé-api-pennylane))
- [x] **Power BI Desktop** (optionnel, pour visualisation)

---

## 📥 Installation

### Étape 1 : Cloner le dépôt

```bash
# Via HTTPS
git clone https://github.com/yves34690/Penny.git
cd Penny

# Via SSH (si configuré)
git clone git@github.com:yves34690/Penny.git
cd Penny
```

### Étape 2 : Créer fichier .env

```bash
# Windows
copy .env.example .env
notepad .env

# Linux/Mac
cp .env.example .env
nano .env
```

**⚠️ IMPORTANT : Configurer au minimum ces 2 variables dans `.env` :**

```env
PENNYLANE_API_KEY=votre_cle_api_ici
POSTGRES_PASSWORD=votre_mot_de_passe_securise
```

### Étape 3 : Installer dépendances Python

```bash
pip install -r requirements.txt
```

### Étape 4 : Démarrer PostgreSQL

```bash
docker-compose up -d
```

**Vérification :**

```bash
docker ps
# Vous devriez voir : pennylane_postgres et pennylane_pgadmin
```

### Étape 5 : Premier test

```bash
cd src
python main.py full
```

Si tout fonctionne, vous verrez :
```
================================================================================
ETL Pennylane → PostgreSQL
Mode: FULL
...
✓ Configuration chargée et validée
✓ Connexion réussie
...
```

---

## ⚙️ Configuration

### Obtenir clé API Pennylane

1. Connexion sur [app.pennylane.com](https://app.pennylane.com)
2. **Paramètres** → **API**
3. Cliquer sur **Générer une clé API**
4. Copier la clé
5. Coller dans `.env` : `PENNYLANE_API_KEY=votre_cle`

### Personnaliser les endpoints

Éditer [config.json](config.json) pour activer/désactiver endpoints :

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
      // Ajouter/retirer des endpoints ici
    ]
  }
}
```

### Changer l'intervalle d'actualisation

Dans `.env` :

```env
SCHEDULER_INTERVAL_MINUTES=5  # Au lieu de 10
```

---

## 🚀 Utilisation quotidienne

### Mode manuel (extraction ponctuelle)

#### Extraction complète (toutes les données)

```bash
cd src
python main.py full
```

**Quand utiliser :**
- Première installation
- Après modification des endpoints
- Réinitialisation complète

#### Extraction incrémentielle (nouveaux enregistrements)

```bash
cd src
python main.py incremental
```

**Quand utiliser :**
- Actualisation manuelle rapide
- Test après modification code
- Récupération après erreur

### Mode automatique (planificateur)

```bash
cd src
python scheduler.py
```

**Fonctionnement :**
- Exécution automatique toutes les 10 minutes (configurable)
- Mode incrémentiel (rapide)
- Tourne en continu jusqu'à `Ctrl+C`

**Logs en temps réel :**

```bash
# Dans un autre terminal
type logs\pennylane_etl.log  # Windows
tail -f logs/pennylane_etl.log  # Linux/Mac
```

### Accéder aux données

#### Via pgAdmin (interface web)

[http://localhost:5050](http://localhost:5050)

- Email : `admin@pennylane.local`
- Password : `admin`

Ajouter serveur :
- Host : `postgres`
- Port : `5432`
- Database : `pennylane_data`
- Username : `pennylane_user`
- Password : (voir `.env`)

#### Via Jupyter Notebook

```python
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

# Connexion
engine = create_engine(
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

# Charger table
df = pd.read_sql('SELECT * FROM pennylane.invoices', engine)
print(f"{len(df)} factures chargées")
```

#### Via Power BI

1. **Obtenir les données** → **PostgreSQL**
2. Serveur : `localhost`, Base : `pennylane_data`
3. Schéma : `pennylane`
4. Sélectionner tables nécessaires
5. **Importer** (pas DirectQuery)

---

## 🔄 Maintenance

### Logs et monitoring

#### Consulter logs d'exécution

```bash
# Dernières lignes
type logs\pennylane_etl.log  # Windows
tail logs/pennylane_etl.log  # Linux/Mac

# Suivi temps réel
tail -f logs/pennylane_etl.log  # Linux/Mac
Get-Content logs\pennylane_etl.log -Wait  # PowerShell
```

#### Vérifier logs ETL dans PostgreSQL

```sql
SELECT * FROM pennylane.etl_logs
WHERE status = 'failed'
ORDER BY execution_date DESC;
```

### Sauvegardes

#### Sauvegarder PostgreSQL

```bash
# Créer sauvegarde
docker exec pennylane_postgres pg_dump -U pennylane_user pennylane_data > backup_$(date +%Y%m%d).sql

# Restaurer sauvegarde
docker exec -i pennylane_postgres psql -U pennylane_user pennylane_data < backup_20250107.sql
```

#### Sauvegarder configuration

```bash
# ATTENTION : Ne pas commiter .env sur GitHub !
cp .env .env.backup
```

### Mise à jour du code

```bash
# Récupérer dernières modifications
git pull origin main

# Réinstaller dépendances si nécessaire
pip install -r requirements.txt --upgrade

# Redémarrer PostgreSQL si docker-compose modifié
docker-compose down
docker-compose up -d
```

---

## 🐛 Dépannage

### Erreurs fréquentes

#### 1. "Variable d'environnement PENNYLANE_API_KEY requise"

**Cause :** Fichier `.env` manquant ou mal configuré

**Solution :**
```bash
cp .env.example .env
notepad .env  # Configurer PENNYLANE_API_KEY
```

#### 2. "Erreur connexion PostgreSQL"

**Cause :** Docker pas démarré ou conteneur arrêté

**Solution :**
```bash
docker ps  # Vérifier conteneurs actifs
docker-compose restart postgres
```

#### 3. "Rate limit dépassé (429)"

**Cause :** Trop de requêtes API en peu de temps

**Solution :** Le script gère automatiquement, attendre quelques secondes.

Si problème persiste, réduire dans `.env` :
```env
PENNYLANE_RATE_LIMIT=3.0
```

#### 4. "Aucune donnée extraite"

**Cause :** Endpoint API incorrect ou pas de nouvelles données

**Solution :**
```bash
# Forcer extraction complète
python main.py full

# Vérifier logs
type logs\pennylane_etl.log
```

### Réinitialisation complète

```bash
# 1. Arrêter tout
docker-compose down -v  # -v supprime volumes (données)

# 2. Nettoyer logs
rm -rf logs/*  # Linux/Mac
del /q logs\*  # Windows

# 3. Redémarrer
docker-compose up -d
cd src && python main.py full
```

---

## 🔮 Évolutions futures

### Version actuelle : 1.0

- [x] Extraction API Pennylane
- [x] Stockage PostgreSQL
- [x] Planificateur 10 min
- [x] Gestion .env sécurisée
- [x] Documentation complète

### Prochaines versions

#### v1.1 - Optimisations
- [ ] Parallélisation extraction multi-endpoints
- [ ] Cache local pour réduire appels API
- [ ] Notifications email en cas d'erreur

#### v1.2 - Transformations avancées
- [ ] Bibliothèque transformations réutilisables
- [ ] Calculs analytiques prédéfinis (CA, marges, etc.)
- [ ] Détection anomalies

#### v1.3 - Dashboards
- [ ] Dashboard Streamlit intégré
- [ ] Métriques temps réel
- [ ] Alertes personnalisables

---

## 📞 Support

### Documentation
- **README** : [README.md](README.md)
- **API Pennylane** : [pennylane.readme.io](https://pennylane.readme.io/)

### Contribution
Issues et Pull Requests bienvenues : [github.com/yves34690/Penny/issues](https://github.com/yves34690/Penny/issues)

---

**📝 Ce guide sera mis à jour au fil des développements.**

**Dernière révision :** 2025-10-07 par yves34690
