# 🚀 ETL Pennylane Open-Source

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![GitHub last commit](https://img.shields.io/github/last-commit/yves34690/Penny)](https://github.com/yves34690/Penny/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/yves34690/Penny)](https://github.com/yves34690/Penny/stargazers)

---

## 🎯 En une phrase

**Synchronisez automatiquement vos données Pennylane vers PostgreSQL toutes les 2 heures, transformez-les dans Jupyter Notebooks, et connectez Power BI pour des analyses ultra-rapides.**

---

## ⭐ Pourquoi ce projet ?

### Le problème

Vous êtes **expert-comptable**, **DAF** ou **data analyst** et vous rencontrez ces difficultés :

- **Actualisation Power BI = 30-60 minutes** à cause des transformations lourdes dans Power Query
- **API Pennylane avec cache de 2 heures** pour les données comptables (grand livre, balance)
- **Difficile de personnaliser** les transformations sans maîtriser le langage M de Power Query
- **Impossible de réutiliser** les données transformées ailleurs (Excel, Tableau, Python)

### La solution

Ce projet ETL open-source résout tous ces problèmes :

- ✅ **Actualisation Power BI = 2-5 minutes** (données pré-traitées)
- ✅ **Transformations dans Jupyter Notebooks** (Python, facile à personnaliser)
- ✅ **Synchronisation automatique toutes les 2 heures** (scheduler intelligent)
- ✅ **Données centralisées dans PostgreSQL** (réutilisables partout)
- ✅ **Architecture "Notebooks First"** : modifiez vos notebooks, le scheduler applique automatiquement

---

## 📊 Notre solution vs Power Query : Comparaison

| Critère | **ETL Python + PostgreSQL** ⭐ | **Power Query Direct** |
|---------|-------------------------------|------------------------|
| ⏱️ **Temps actualisation** | **2-5 min** | 30-60 min |
| 🎯 **Performance** | ⭐⭐⭐⭐⭐ Très rapide | ⭐⭐ Lent |
| 📊 **Gros volumes** | ✅ Millions de lignes | ❌ ~500k lignes max |
| 🔄 **Réutilisabilité** | ✅ Excel, Tableau, Python | ❌ Uniquement Power BI |
| 👥 **Collaboration** | ✅ Base centralisée | ❌ Fichier .pbix par personne |
| 🎨 **Personnalisation** | ✅ Jupyter (visuel) | ⚠️ Langage M (complexe) |
| 🔧 **Maintenance** | ✅ 1 modification → tous en profitent | ❌ Modifier chaque .pbix |
| 💾 **Charge Power BI** | Minimale | Très élevée |
| 📈 **Scalabilité** | ⭐⭐⭐⭐⭐ (serveur) | ⭐⭐ (PC utilisateur) |
| 🔄 **Fréquence actualisation** | Toutes les 2h automatique | Manuel ou 8x/jour max |

**💡 Cas d'usage réel** : Cabinet avec 200k lignes comptables
- **Sans ETL** : 45 min d'actualisation, PC bloqué
- **Avec ETL** : 3 min d'actualisation, PC libre
- **Gain** : **42 minutes × 10 actualisations/jour = 7h gagnées/jour** ⏱️

**👉 Voir comparaison complète** : [GUIDE_POWERBI_CONNEXION.md](GUIDE_POWERBI_CONNEXION.md#1-etl-pythonpostgresql-vs-power-query--quel-choix-)

---

## 🎓 Accessible à TOUS

Ce projet est conçu pour être utilisable **sans connaissance en programmation**.

| Profil | Utilisation | Documentation |
|--------|-------------|---------------|
| 🆕 **Débutant complet** | Guide pas-à-pas avec captures d'écran | 👉 **[DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md)** ⭐ |
| 👔 **Expert-comptable / DAF** | Personnaliser transformations via Jupyter Notebooks | [README_NOTEBOOK_SCHEDULER.md](README_NOTEBOOK_SCHEDULER.md) |
| 📊 **Data Analyst** | Modifier notebooks Python, ajouter colonnes calculées | [README_NOTEBOOK_SCHEDULER.md](README_NOTEBOOK_SCHEDULER.md) |
| 🐍 **Développeur Python** | Comprendre architecture, automatisation Docker | [GUIDE_AUTOMATION.md](GUIDE_AUTOMATION.md) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PENNYLANE                              │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │   API REST       │         │  Data Sharing    │        │
│  │ (5 tables temps  │         │  (Redshift)      │        │
│  │  réel)           │         │  (comptabilité)  │        │
│  └────────┬─────────┘         └────────┬─────────┘        │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            └──────────────┬───────────────┘
                           │
                  📥 EXTRACTION (2h)
                           │
            ┌──────────────▼───────────────┐
            │   NOTEBOOK SCHEDULER         │
            │   (src/notebook_scheduler.py)│
            │   Exécute 16 notebooks       │
            └──────────────┬───────────────┘
                           │
            ┌──────────────▼───────────────────────────────┐
            │      JUPYTER NOTEBOOKS                       │
            │      (data/API Publique/*.ipynb)             │
            │  ┌─────────────────────────────────────┐    │
            │  │ 1. Import_customers.ipynb           │    │
            │  │ 2. Import_analytical_ledger.ipynb   │    │
            │  │ 3. Import_general_ledger.ipynb      │    │
            │  │ ... 16 notebooks au total           │    │
            │  │                                      │    │
            │  │ 🎨 VOUS MODIFIEZ ICI :              │    │
            │  │    - Ajout colonnes calculées       │    │
            │  │    - Transformations métier         │    │
            │  │    - Filtres personnalisés          │    │
            │  └─────────────────────────────────────┘    │
            └──────────────┬───────────────────────────────┘
                           │
                  💾 CHARGEMENT
                           │
            ┌──────────────▼───────────────┐
            │   POSTGRESQL (Docker)        │
            │   Schema: pennylane          │
            │   12 tables transformées     │
            └──────────────┬───────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
        ┌───────▼───────┐     ┌──────▼──────┐
        │   POWER BI    │     │   JUPYTER   │
        │   Desktop     │     │   Excel     │
        └───────────────┘     └─────────────┘
```

**Philosophie "Notebooks First"** :
1. Vous modifiez un notebook Jupyter (ajout colonnes, calculs)
2. Vous testez et visualisez immédiatement
3. Le scheduler applique automatiquement vos changements toutes les 2h
4. Power BI se connecte aux données finales

**➡️ Aucune duplication de code !** Les notebooks sont la **seule source de vérité**.

---

## ⚡ Quick Start (5 minutes)

### Prérequis

- **Windows, Mac ou Linux**
- **Python 3.12+** installé
- **Docker Desktop** installé ([Guide installation](GUIDE_INSTALLATION_DOCKER.md))

### 🖥️ Comment ouvrir un terminal ?

**Pour exécuter les commandes ci-dessous, vous devez ouvrir un terminal :**

**Sur Windows** :
1. Appuyez sur la touche **Windows**
2. Tapez `PowerShell`
3. Cliquez sur **Windows PowerShell**
4. Une fenêtre bleue s'ouvre → c'est votre terminal !

**Sur Mac** :
1. Appuyez sur **Cmd + Espace**
2. Tapez `Terminal`
3. Appuyez sur **Entrée**

**Sur Linux** :
- Appuyez sur **Ctrl + Alt + T**

---

### Installation

**Dans votre terminal**, tapez ces commandes une par une :

```bash
# 1. Cloner le projet
git clone https://github.com/yves34690/Penny.git
cd Penny

# 2. Installer dépendances Python
pip install -r requirements.txt

# 3. Configurer vos credentials
cp .env.example .env
# Ouvrez le fichier .env avec un éditeur de texte (Notepad, VS Code)
# et ajoutez vos clés Pennylane

# 4. Démarrer le système complet (PostgreSQL + Scheduler automatique)
docker-compose up -d

# 5. Vérifier que tout est OK (optionnel mais recommandé)
python verify_setup.py
```

**✅ C'est tout !** Le système est maintenant **100% automatique** :
- ✅ PostgreSQL démarré sur le port 5433
- ✅ Scheduler automatique en cours d'exécution
- ✅ Synchronisation initiale en cours (8 min)
- ✅ Prochaine synchronisation dans 2 heures

**📊 Suivre les logs en temps réel** :
```bash
docker-compose logs scheduler -f
```
*Appuyez sur Ctrl + C pour arrêter l'affichage*

**🔧 Arrêter le système** :
```bash
docker-compose down
```

**🔄 Redémarrer après un reboot du PC** :
```bash
cd C:\Penny && docker-compose up -d
```

**🎯 Pour plus de détails sur l'automatisation** : Voir [GUIDE_AUTOMATION.md](GUIDE_AUTOMATION.md)

### 🔍 Vérification de la configuration

Le script `verify_setup.py` vérifie automatiquement :
- ✅ Fichier `.env` présent et correctement configuré
- ✅ Docker démarré (PostgreSQL + pgAdmin)
- ✅ Connexion PostgreSQL fonctionnelle
- ✅ Connexion Redshift (Data Warehouse Pennylane)
- ✅ Packages Python installés
- ✅ Notebooks présents

**Si tout est vert**, vous pouvez lancer le scheduler en toute confiance !

### Connexion Power BI

```
Power BI Desktop
→ Obtenir les données
→ PostgreSQL
→ Serveur: localhost:5433
→ Base: pennylane_db
→ Sélectionner schema "pennylane"
```

**Guide complet** : [GUIDE_POWERBI_CONNEXION.md](GUIDE_POWERBI_CONNEXION.md)

---

## 🤖 Automatisation complète avec Docker

### Mode automatique (Recommandé)

**Une seule commande** pour tout démarrer :

```bash
docker-compose up -d
```

**Ce qui se passe automatiquement** :
1. ✅ PostgreSQL démarre (port 5433)
2. ✅ pgAdmin démarre ([http://localhost:5050](http://localhost:5050))
3. ✅ Le scheduler s'exécute immédiatement (première synchronisation)
4. ✅ Ensuite, synchronisation automatique toutes les 2 heures
5. ✅ Redémarrage automatique en cas de crash ou reboot PC

**Aucune intervention nécessaire !** Le système tourne en arrière-plan 24/7.

### Vérifier que tout fonctionne

```bash
# État des conteneurs
docker-compose ps

# Logs en temps réel du scheduler
docker-compose logs scheduler -f

# Logs depuis le dernier démarrage
docker-compose logs scheduler --tail 100
```

**Sortie attendue** :
```
[DEMARRAGE] Notebook Scheduler Pennylane
[SYNC] DEBUT synchronisation
[OK] customers: 7 lignes exportées
[OK] analytical_ledger: 2251 lignes exportées
...
[SYNC] Succès: 12/12 | Erreurs: 0
[CRON] Prochaine exécution dans 2h
```

### Gestion du système

```bash
# Arrêter tout
docker-compose down

# Redémarrer
docker-compose restart

# Forcer une synchronisation immédiate
docker-compose restart scheduler
```

**📖 Documentation complète** : [GUIDE_AUTOMATION.md](GUIDE_AUTOMATION.md)

---

## 📂 Structure du projet (simplifiée)

```
Penny/
├── 📄 .env.example                      # Template credentials (à copier)
├── 📄 .env                              # VOS secrets (jamais commité)
├── 🐳 docker-compose.yml                # PostgreSQL + pgAdmin
├── 📦 requirements.txt                  # Dépendances Python
│
├── 📁 src/
│   ├── 🤖 notebook_scheduler.py         # ⭐ SCHEDULER PRINCIPAL (exécute notebooks)
│   └── 🔌 pennylane_api_client.py       # Client API Pennylane
│
├── 📁 data/API Publique/
│   ├── 📓 Import_customers.ipynb        # 🎨 NOTEBOOKS À PERSONNALISER
│   ├── 📓 Import_analytical_ledger.ipynb
│   ├── 📓 Import_general_ledger.ipynb
│   └── ... (16 notebooks au total)
│
├── 📁 logs/
│   ├── executed_notebooks/              # Historique exécutions notebooks
│   └── notebook_scheduler.log           # Logs du scheduler
│
└── 📚 Documentation/
    ├── GUIDE_DEBUTANT.md                # 🆕 Démarrage sans code
    ├── README_NOTEBOOK_SCHEDULER.md     # Architecture "Notebooks First"
    ├── CHOIX_SCHEDULER.md               # Notebook vs Unified scheduler
    ├── GUIDE_INSTALLATION_DOCKER.md     # Installer Docker pas-à-pas
    └── GUIDE_POWERBI_CONNEXION.md       # Connecter Power BI + Comparaison ETL vs Power Query
```

**✨ Seulement ~25 fichiers essentiels** (nettoyé de tout superflu)

---

## 🎯 Tables disponibles

| Table | Source | Description | Lignes (exemple) |
|-------|--------|-------------|------------------|
| **customers** | API REST | Clients | 7 |
| **suppliers** | API REST | Fournisseurs | 50 |
| **customer_invoices** | API REST | Factures clients | 12 |
| **supplier_invoices** | API REST | Factures fournisseurs | 273 |
| **bank_accounts** | API REST | Comptes bancaires | 5 |
| **analytical_ledger** | Redshift | Grand livre analytique | 2 251 |
| **general_ledger** | Redshift | Grand livre général | 2 233 |
| **trial_balance** | Redshift | Balance générale | 163 |
| **bank_transactions** | Redshift | Transactions bancaires | 325 |
| **fiscal_years** | Redshift | Exercices fiscaux | 3 |
| **tax_declarations** | Redshift | Déclarations fiscales | 12 |
| **vat_declarations** | Redshift | Déclarations TVA | 18 |

**Total : 12 tables** (transformées avec colonnes calculées : PCG_1, PCG_2, Nature_Compte, Solde, etc.)

---

## 🔐 Sécurité des credentials

### Architecture

- **`.env.example`** : Template public (committé sur GitHub)
- **`.env`** : VOS secrets (ignoré par Git, **jamais commité**)

### Variables obligatoires

Copiez `.env.example` vers `.env` et configurez :

```bash
# Pennylane API REST (5 tables temps réel)
PENNYLANE_API_TOKEN=votre_token_api_rest

# Pennylane Data Sharing (Redshift, 7 tables comptables)
PENNYLANE_DATA_SHARING_KEY=votre_cle_redshift
REDSHIFT_HOST=redshift-pennylane.123456789.eu-west-1.redshift.amazonaws.com
REDSHIFT_PORT=5439
REDSHIFT_DATABASE=votre_database
REDSHIFT_USER=votre_user

# PostgreSQL local (Docker)
POSTGRES_USER=pennylane_user
POSTGRES_PASSWORD=votre_mot_de_passe_securise
POSTGRES_DB=pennylane_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

**⚠️ Important** : Le fichier `.gitignore` est configuré pour **ne jamais commiter `.env`**.

---

## 🎨 Personnaliser vos transformations

### Étape 1 : Ouvrir Jupyter

```bash
jupyter notebook
```

### Étape 2 : Modifier un notebook

Exemple : Ajouter une colonne dans `Import_analytical_ledger.ipynb`

```python
# Charger données brutes depuis Redshift
df = pd.read_sql("SELECT * FROM analytical_ledger", redshift_engine)

# 🎨 AJOUTEZ VOS TRANSFORMATIONS ICI
df['montant_ht_euros'] = df['amount_cents'] / 100
df['trimestre'] = df['date'].dt.quarter
df['est_achat'] = df['PCG_1'] == '6'

# Sauvegarder dans PostgreSQL
df.to_sql('analytical_ledger', postgres_engine,
          schema='pennylane', if_exists='replace', index=False)
```

### Étape 3 : Tester immédiatement

**Cell** → **Run All** : Vous voyez le résultat instantanément

### Étape 4 : Le scheduler applique automatiquement

```bash
python src/notebook_scheduler.py
```

À chaque exécution (toutes les 2h), **votre notebook modifié est exécuté** et PostgreSQL est mis à jour.

**✅ Aucune modification de code Python nécessaire !** Le scheduler détecte automatiquement vos notebooks.

---

## 📊 Utilisation

### ⭐ Mode 1 : Docker Automatique (Recommandé pour production)

```bash
# Démarrer le système complet
docker-compose up -d
```

**Avantages** :
- ✅ Synchronisation automatique toutes les 2 heures
- ✅ Redémarrage automatique en cas d'erreur
- ✅ Redémarre au boot (si Docker Desktop configuré)
- ✅ Pas besoin de garder un terminal ouvert

**Suivre l'exécution** :
```bash
docker-compose logs scheduler -f
```

**Arrêter** :
```bash
docker-compose down
```

📖 **Documentation complète** : [GUIDE_AUTOMATION.md](GUIDE_AUTOMATION.md)

---

### Mode 2 : Python manuel (pour tests ou développement)

#### 2a. Synchronisation unique

```bash
# Exécuter une fois tous les notebooks (8 min)
python src/notebook_scheduler.py
```

**Arrêter après 1 synchro** : `Ctrl+C`

#### 2b. Synchronisation continue

```bash
# Lancer en continu (synchro toutes les 2h)
python src/notebook_scheduler.py
# Laisser tourner dans le terminal
```

**Logs en temps réel** :

```
[2025-10-15 14:00:00] 🚀 Démarrage du Notebook Scheduler
[2025-10-15 14:00:05] ✅ customers - 7 lignes chargées
[2025-10-15 14:01:20] ✅ analytical_ledger - 2251 lignes chargées
...
[2025-10-15 14:08:15] 🎉 Synchronisation complète terminée (8m 15s)
[2025-10-15 14:08:15] ⏰ Prochaine synchro : 2025-10-15 16:00:00
```

**Arrêter** : `Ctrl+C`

**Inconvénient** : Vous devez laisser le terminal ouvert. Si vous le fermez, la synchro s'arrête.

---

### Mode 3 : Exécuter un seul notebook

```bash
# Lancer Jupyter
jupyter notebook

# Ouvrir data/API Publique/Import_customers.ipynb
# Cell → Run All
```

---

## 🔧 Gestion PostgreSQL

### Interface graphique pgAdmin

**URL** : [http://localhost:5050](http://localhost:5050)

**Credentials** (par défaut) :
- Email : `admin@pennylane.local`
- Password : `admin`

### Connexion serveur PostgreSQL

1. **Clic droit** sur "Servers" → **Register** → **Server**
2. **Onglet General** :
   - Name : `Pennylane Local`
3. **Onglet Connection** :
   - Host : `postgres` (nom du conteneur Docker)
   - Port : `5432` (port interne Docker)
   - Database : `pennylane_db`
   - Username : `pennylane_user`
   - Password : (voir `.env`)

### Requêtes SQL utiles

```sql
-- Lister les tables
SELECT table_name,
       pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
FROM information_schema.tables
WHERE table_schema = 'pennylane'
ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;

-- Voir un aperçu
SELECT * FROM pennylane.analytical_ledger LIMIT 10;

-- Compter lignes
SELECT 'customers' AS table, COUNT(*) FROM pennylane.customers
UNION ALL
SELECT 'analytical_ledger', COUNT(*) FROM pennylane.analytical_ledger
UNION ALL
SELECT 'general_ledger', COUNT(*) FROM pennylane.general_ledger;
```

---

## 🐛 Dépannage

### 🔍 Première étape : Lancer le diagnostic automatique

```bash
python verify_setup.py
```

Ce script vérifie automatiquement tous les composants et affiche les erreurs éventuelles.

---

### ❌ Erreur : "Module 'papermill' not found"

**Solution** :
```bash
pip install -r requirements.txt
```

### ❌ Erreur : "Cannot connect to PostgreSQL"

**Diagnostic** :
```bash
docker ps
# Doit afficher 2 conteneurs "Up" (postgres + pgadmin)
```

**Solution** :
```bash
docker-compose restart
```

### ❌ Erreur API Pennylane : "Unauthorized"

**Solution** : Vérifier `.env` :
- `PENNYLANE_API_TOKEN` (API REST)
- `PENNYLANE_DATA_SHARING_KEY` (Redshift)

### ❌ Notebook échoue : "Table does not exist"

**Cause** : Mauvais credentials Redshift dans `.env`

**Solution** : Tester connexion Redshift manuellement :
```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(
    host=os.getenv('REDSHIFT_HOST'),
    port=os.getenv('REDSHIFT_PORT'),
    database=os.getenv('REDSHIFT_DATABASE'),
    user=os.getenv('REDSHIFT_USER'),
    password=os.getenv('PENNYLANE_DATA_SHARING_KEY')
)
print("✅ Connexion Redshift OK")
```

### Voir les logs complets

```bash
# Windows
type logs\notebook_scheduler.log

# Linux/Mac
cat logs/notebook_scheduler.log
```

---

## ⚖️ Notebook Scheduler vs Unified Scheduler

Ce projet propose **2 schedulers** :

| Critère | **Notebook Scheduler** ⭐ | **Unified Scheduler** |
|---------|---------------------------|----------------------|
| **Source de vérité** | Notebooks Jupyter | Code Python dupliqué |
| **Maintenance** | 1 seul endroit | 2 endroits (notebook + .py) |
| **Personnalisation** | ⭐⭐⭐⭐⭐ Très facile | ⭐⭐⭐ Moyen |
| **Public cible** | Tous (y compris non-devs) | Développeurs Python |
| **Performance** | ~10-12 min | ~8 min |

**👉 Recommandé** : **Notebook Scheduler** (philosophie de ce projet open-source)

**Voir comparaison complète** : [CHOIX_SCHEDULER.md](CHOIX_SCHEDULER.md)

---

## 🤝 Contribution

Ce projet est **open-source** et conçu pour être **forkable** facilement.

### Partager votre fork

1. **NE JAMAIS** commiter `.env` (vos secrets)
2. Mettre à jour `.env.example` si nouvelles variables
3. Documenter vos transformations dans les notebooks

### Déploiement chez un client

```bash
# 1. Cloner
git clone https://github.com/votre-username/Penny.git
cd Penny

# 2. Créer .env
cp .env.example .env
nano .env  # Configurer credentials du client

# 3. Démarrer
docker-compose up -d
pip install -r requirements.txt
python src/notebook_scheduler.py
```

### Ajouter un nouvel endpoint

1. **Créer notebook** : `data/API Publique/Import_nouvelle_table.ipynb`
2. **Le scheduler le détecte automatiquement** (aucune modification code !)
3. **Tester** : Exécuter le notebook manuellement dans Jupyter
4. **Déployer** : Le scheduler l'inclura à la prochaine synchro

---

## 📝 Licence

**MIT License** - Libre d'utilisation, modification et redistribution.

Voir [LICENSE](LICENSE) pour détails.

---

## 📞 Support et communauté

- **Documentation Pennylane API** : [pennylane.readme.io](https://pennylane.readme.io/)
- **Issues GitHub** : [github.com/yves34690/Penny/issues](https://github.com/yves34690/Penny/issues)
- **Documentation complète** : Voir guides dans le projet

---

## 🌟 Remerciements

Projet créé pour la **communauté Pennylane** francophone.

Contributions bienvenues ! ⭐

---

**Auteur** : Yves Cloarec
**Version** : 3.0 (Architecture "Notebooks First")
**Date** : Octobre 2025
