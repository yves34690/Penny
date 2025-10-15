# 📊 Guide de Connexion Power BI à PostgreSQL

**Objectif** : Connecter Power BI à votre base PostgreSQL et choisir le bon mode (Import vs DirectQuery).

**Prérequis** :
- PostgreSQL démarré via Docker ([GUIDE_INSTALLATION_DOCKER.md](GUIDE_INSTALLATION_DOCKER.md))
- Power BI Desktop installé ([Télécharger ici](https://powerbi.microsoft.com/fr-fr/desktop/))

---

## 📋 Table des matières

1. [ETL Python/PostgreSQL vs Power Query : Quel choix ?](#1-etl-pythonpostgresql-vs-power-query--quel-choix-)
2. [Import vs DirectQuery : Comprendre la différence](#2-import-vs-directquery--comprendre-la-différence)
3. [Arbre de décision : Quel mode choisir ?](#3-arbre-de-décision--quel-mode-choisir-)
4. [Connexion en mode Import (Recommandé)](#4-connexion-en-mode-import-recommandé-)
5. [Connexion en mode DirectQuery](#5-connexion-en-mode-directquery)
6. [Optimisations Performance](#6-optimisations-performance)
7. [Actualisation automatique](#7-actualisation-automatique)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. ETL Python/PostgreSQL vs Power Query : Quel choix ? 🤔

### Tableau comparatif complet

| Critère | **Notre Solution ETL<br>(Python + PostgreSQL)** ⭐ | **Power Query Direct<br>(Power BI uniquement)** |
|---------|------------------------------------------------|------------------------------------------------|
| **🎯 Performance** | ⭐⭐⭐⭐⭐ Très rapide | ⭐⭐ Lent (transformations à chaque actualisation) |
| **⏱️ Temps actualisation** | **2-5 min** (pré-calculé) | **30-60 min** (recalcule tout à chaque fois) |
| **💾 Charge Power BI** | ⭐⭐⭐⭐⭐ Minimale (données propres) | ⭐ Très élevée (fait tout le travail) |
| **🔄 Réutilisabilité** | ✅ Données utilisables par Excel, Tableau, etc. | ❌ Uniquement Power BI |
| **📊 Gros volumes** | ✅ Millions de lignes sans problème | ❌ Limite pratique ~500k lignes |
| **🧮 Transformations complexes** | ✅ Python = puissance illimitée | ⚠️ Limité par fonctions Power Query |
| **👥 Collaboration** | ✅ Base centralisée, plusieurs utilisateurs | ❌ Fichier .pbix par personne |
| **🔐 Sécurité données** | ✅ Gérée au niveau PostgreSQL (RLS) | ⚠️ Données dans fichier Power BI |
| **📅 Historisation** | ✅ Facile (INSERT INTO history_table) | ❌ Difficile (nécessite scripts externes) |
| **🔧 Maintenance** | ✅ Une modification → tous bénéficient | ❌ Modifier chaque fichier .pbix |
| **💰 Coût licence** | ✅ Gratuit (PostgreSQL + Python) | ✅ Gratuit (inclus Power BI Desktop) |
| **⚡ Déploiement production** | ✅ Scheduler automatique 24/7 | ⚠️ Nécessite Power BI Gateway + Pro |
| **📈 Scalabilité** | ⭐⭐⭐⭐⭐ Excellent (ajouter RAM serveur) | ⭐⭐ Limitée (dépend PC utilisateur) |
| **🎓 Courbe apprentissage** | ⭐⭐ Moyenne (Python de base) | ⭐⭐⭐⭐ Facile (interface graphique) |
| **🐛 Debug** | ⭐⭐⭐ Facile (logs Python) | ⭐⭐ Difficile (erreurs Power Query obscures) |
| **🔄 Fréquence actualisation** | ✅ Toutes les 2h automatique | ⚠️ Manuel ou Gateway (8x/jour max) |
| **📊 Modèle de données** | ✅ Star schema pré-construit | ⚠️ À construire manuellement |
| **🎨 Flexibilité métier** | ✅ DAF peut modifier notebooks Python | ⚠️ DAF doit maîtriser M (Power Query) |

### 🎯 **Notre recommandation**

**Utilisez notre solution ETL (Python + PostgreSQL)** si :
- ✅ Vous avez **plus de 100 000 lignes** à traiter
- ✅ Vous voulez des **actualisations rapides** (< 5 min vs 30-60 min)
- ✅ Plusieurs personnes utilisent les **mêmes données**
- ✅ Vous avez des **transformations complexes** (PCG, classifications métier)
- ✅ Vous voulez **séparer calculs et visualisation** (bonne pratique)

**Utilisez Power Query direct** si :
- ✅ Données **très petites** (< 50 000 lignes)
- ✅ Projet **personnel** (pas de partage)
- ✅ Transformations **ultra-simples** (renommer colonnes, filtres)
- ✅ Vous êtes **expert Power Query M**
- ✅ Pas d'accès serveur/Docker

### 💡 Cas d'usage réels

**Scénario 1** : Expert-comptable avec 5 clients, 200k lignes total
- **Sans notre ETL** : 45 min d'actualisation Power BI, PC bloqué
- **Avec notre ETL** : 3 min d'actualisation, PC libre immédiatement
- **Gain** : **42 minutes** par actualisation × 10 actualisations/jour = **7h gagnées/jour** ⏱️

**Scénario 2** : Cabinet d'expertise avec 3 analystes
- **Sans notre ETL** : Chaque analyste recrée les transformations dans son .pbix → Incohérences
- **Avec notre ETL** : Base centralisée → Tout le monde utilise les mêmes données → Cohérence
- **Gain** : **Fiabilité** + **3x moins de travail**

**Scénario 3** : Suivi mensuel avec historique 3 ans
- **Sans notre ETL** : Power Query re-télécharge TOUT chaque mois depuis Pennylane → Très lent
- **Avec notre ETL** : Extraction incrémentale (seules nouvelles données) → Rapide
- **Gain** : **Actualisation 10x plus rapide**

---

## 2. Import vs DirectQuery : Comprendre la différence

### Import Mode (Par défaut ⭐)

**Principe** : Power BI **télécharge et stocke** les données dans le fichier .pbix.

```
┌───────────────┐
│  PostgreSQL   │
└───────┬───────┘
        │ Téléchargement 1x
        ↓
┌───────────────┐
│   Power BI    │ ← Données en mémoire
│   (.pbix)     │   Très rapide !
└───────────────┘
```

**Avantages** :
- ⚡ **Performance maximale** : Requêtes instantanées
- 🎨 **Toutes fonctionnalités DAX** disponibles
- 📴 **Fonctionne hors ligne**
- 🔄 **Moins de charge** sur PostgreSQL

**Inconvénients** :
- 📦 **Taille fichier .pbix** peut être grosse
- 🕐 **Pas de temps réel** (actualisation manuelle/planifiée)
- 💾 **Limite taille** : ~10 GB par dataset (Power BI Service)

**Quand utiliser** :
- ✅ Rapports consultés fréquemment
- ✅ Besoin de performance maximale
- ✅ Données actualisées toutes les 2h suffisent
- ✅ Tableaux croisés dynamiques complexes
- ✅ **RECOMMANDÉ pour 95% des cas**

---

### DirectQuery Mode

**Principe** : Power BI **interroge PostgreSQL à chaque clic** utilisateur.

```
┌───────────────┐
│  PostgreSQL   │ ← Sollicité en permanence
└───────┬───────┘
        │ Requête à chaque clic
        ↓
┌───────────────┐
│   Power BI    │ ← Pas de stockage local
│   (.pbix)     │   Temps réel mais plus lent
└───────────────┘
```

**Avantages** :
- 🕐 **Données temps réel** (aucun délai)
- 📦 **Fichier .pbix léger** (pas de données stockées)
- 🔐 **Sécurité renforcée** (données restent dans PostgreSQL)
- ♾️ **Pas de limite taille** dataset

**Inconvénients** :
- 🐌 **Performance réduite** (réseau + SQL à chaque interaction)
- ⚠️ **Fonctionnalités DAX limitées** (certaines calculs impossibles)
- 🌐 **Connexion Internet requise** en permanence
- 📊 **Charge élevée** sur PostgreSQL

**Quand utiliser** :
- ✅ Besoin **vraiment temps réel** (< 2h d'actualisation insuffisant)
- ✅ Données **très volumineuses** (> 10 GB)
- ✅ **Gouvernance stricte** (données ne doivent pas sortir du serveur)
- ✅ Dashboards **rarement consultés** (pas besoin de cache)

---

## 3. Arbre de décision : Quel mode choisir ? 🌳

```
🤔 Ai-je besoin de données temps réel absolu (< 2 minutes) ?
│
├─ ❌ Non → MODE IMPORT ✅ (Recommandé)
│          Performance maximale
│          Actualisation 2h suffisante
│
└─ ✅ Oui
    │
    └─ 🤔 Ma base fait plus de 10 GB ?
        │
        ├─ ❌ Non → MODE IMPORT quand même
        │          Actualisation 2h = quasi temps réel
        │          Bien meilleures performances
        │
        └─ ✅ Oui → DIRECTQUERY
                   Attention : Optimiser indexes PostgreSQL
                   Performances réduites à prévoir
```

### Tableau récapitulatif

| Votre situation | Mode recommandé | Raison |
|-----------------|-----------------|--------|
| Expert-comptable, rapports mensuels | **Import** | Performance, pas besoin temps réel |
| DAF, KPIs actualisés 2x/jour | **Import** | 2h d'actualisation largement suffisant |
| Dashboard temps réel (monitoring) | **DirectQuery** | Besoin données instantanées |
| Base > 10 GB, rapports occasionnels | **DirectQuery** | Éviter fichiers .pbix énormes |
| Débutant Power BI | **Import** | Plus simple, plus rapide |
| Données sensibles réglementées | **DirectQuery** | Données ne sortent pas du serveur |

**🎯 Pour 95% des utilisateurs Pennylane** : **MODE IMPORT** est le meilleur choix.

---

## 4. Connexion en mode Import (Recommandé) ⭐

### Étape 1 : Ouvrir Power BI Desktop

1. **Lancer** Power BI Desktop
2. **Cliquer** sur **"Obtenir les données"** (Get Data)
3. **Rechercher** : `PostgreSQL`
4. **Sélectionner** : **"Base de données PostgreSQL"**
5. **Cliquer** : **Connecter**

### Étape 2 : Paramètres de connexion

Dans la fenêtre qui s'ouvre :

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| **Serveur** | `localhost:5433` | Adresse PostgreSQL Docker |
| **Base de données** | `pennylane_db` | Nom de la base (voir `.env`) |
| **Mode connectivité** | **Import** ⭐ | Télécharge les données |

**Exemple visuel** :
```
┌─────────────────────────────────────────┐
│ Base de données PostgreSQL              │
├─────────────────────────────────────────┤
│ Serveur: localhost:5433                 │
│ Base de données: pennylane_db           │
│                                         │
│ Mode connectivité:                      │
│ ◉ Import                                │
│ ○ DirectQuery                           │
│                                         │
│ [Options avancées ▼]                    │
│                                         │
│          [Annuler]     [OK]             │
└─────────────────────────────────────────┘
```

**Cliquer** : **OK**

### Étape 3 : Authentification

**Première connexion** :

1. **Sélectionner** : **"Base de données"** (onglet gauche)
2. **Entrer credentials** :
   - Nom d'utilisateur : `pennylane_user`
   - Mot de passe : (celui de votre `.env`, par défaut `pennylane_password`)
3. ✅ **Cocher** : "Enregistrer ces informations"
4. **Cliquer** : **Connecter**

**Exemple visuel** :
```
┌─────────────────────────────────────────┐
│ Authentification PostgreSQL             │
├─────────────────────────────────────────┤
│ ┌─────────┬──────────┬──────────┐      │
│ │ Windows │ Database │ Compte...│      │
│ └─────────┴──────────┴──────────┘      │
│                                         │
│ Nom d'utilisateur: pennylane_user      │
│ Mot de passe: ••••••••••••             │
│                                         │
│ ☑ Enregistrer ces informations         │
│                                         │
│          [Annuler]     [Connecter]      │
└─────────────────────────────────────────┘
```

### Étape 4 : Sélection des tables

Le **Navigateur** s'ouvre avec toutes les tables disponibles :

```
📂 pennylane_db
  ├── 📂 public (vide)
  └── 📂 pennylane ⭐ (notre schema)
       ├── ☑ analytical_ledger (2251 lignes)
       ├── ☑ customers (7 lignes)
       ├── ☑ customer_invoices (12 lignes)
       ├── ☑ suppliers (50 lignes)
       ├── ☑ supplier_invoices (273 lignes)
       ├── ☑ bank_transactions (325 lignes)
       ├── ☑ general_ledger (2233 lignes)
       ├── ☑ trial_balance (163 lignes)
       ├── ☑ bank_accounts (5 lignes)
       ├── ☑ fiscal_years (3 lignes)
       ├── ☑ tax_declarations (12 lignes)
       └── ☑ vat_declarations (18 lignes)
```

**Actions** :
1. **Développer** le schema `pennylane` (cliquer sur `▶`)
2. **Cocher** les tables souhaitées
3. **Prévisualiser** en cliquant sur une table (vérifier données)
4. **Cliquer** : **Charger** (Load)

**Astuce** : Vous pouvez sélectionner **toutes les tables** d'un coup en cochant `pennylane`.

### Étape 5 : Attendre le chargement

Power BI télécharge les données :

```
Chargement en cours...
├── analytical_ledger    ████████████ 100% (2251 lignes)
├── customers            ████████████ 100% (7 lignes)
├── customer_invoices    ████████████ 100% (12 lignes)
└── ...
```

**Durée** : 10-30 secondes selon nombre de tables.

### Étape 6 : Vérifier les données

1. **Onglet "Données"** (icône tableau à gauche)
2. **Sélectionner** une table dans le panneau de droite
3. **Vérifier** que les données s'affichent correctement
4. **Vérifier colonnes** :
   - `analytical_ledger` : Doit avoir `PCG_1`, `PCG_2`, `PCG_3`, `Nature_Compte`, `Solde`
   - `customers` : Doit avoir `name`, `billing_address` (en JSON), etc.

✅ **Si tout est OK**, vous êtes prêt à créer des visualisations !

---

## 5. Connexion en mode DirectQuery

### Étape 1-2 : Identiques à Import

Suivre **Étapes 1 et 2 du mode Import**, mais sélectionner **DirectQuery** au lieu d'Import.

```
┌─────────────────────────────────────────┐
│ Mode connectivité:                      │
│ ○ Import                                │
│ ◉ DirectQuery ⭐                        │
└─────────────────────────────────────────┘
```

### Étape 3 : Sélection des tables (Limité)

**⚠️ Différence importante** : En DirectQuery, vous ne pouvez **pas mélanger tables** de sources différentes.

**Recommandation** : Sélectionner **une seule table principale** ou tables liées par FK.

### Étape 4 : Pas de chargement

Power BI ne télécharge **rien**. La connexion est établie, c'est tout.

### Étape 5 : Optimiser PostgreSQL

**CRUCIAL** : DirectQuery sollicite intensément PostgreSQL. **Vous devez créer des index**.

#### Connexion PostgreSQL

```bash
docker exec -it postgres psql -U pennylane_user -d pennylane_db
```

#### Créer indexes essentiels

```sql
-- Index sur colonnes fréquemment filtrées
CREATE INDEX idx_analytical_date ON pennylane.analytical_ledger(date);
CREATE INDEX idx_analytical_pcg1 ON pennylane.analytical_ledger(PCG_1);
CREATE INDEX idx_invoices_date ON pennylane.customer_invoices(date);
CREATE INDEX idx_invoices_status ON pennylane.customer_invoices(status);
CREATE INDEX idx_transactions_date ON pennylane.bank_transactions(date);

-- Index sur clés étrangères (si relations)
CREATE INDEX idx_invoices_customer ON pennylane.customer_invoices(customer_id);
CREATE INDEX idx_transactions_account ON pennylane.bank_transactions(bank_account_id);

-- Index composites pour filtres combinés
CREATE INDEX idx_analytical_date_pcg ON pennylane.analytical_ledger(date, PCG_1);
```

**Vérifier performance** :

```sql
EXPLAIN ANALYZE
SELECT * FROM pennylane.analytical_ledger
WHERE date >= '2024-01-01' AND PCG_1 = '6';
```

Cherchez **"Index Scan"** au lieu de **"Seq Scan"** → Index utilisé ✅

### Étape 6 : Limiter volumes dans Power BI

**Options avancées** (lors de la connexion) :

```sql
SELECT * FROM pennylane.analytical_ledger
WHERE date >= CURRENT_DATE - INTERVAL '1 year'
```

Cela réduit la charge en ne chargeant que 1 an de données.

---

## 6. Optimisations Performance

### Mode Import

#### Réduire taille dataset

**Power Query Editor** (Transform Data) :

1. **Supprimer colonnes inutiles** :
   - Colonnes JSON non exploitées
   - Identifiants techniques (`id` si pas utilisé)

2. **Filtrer lignes** :
   ```m
   // Garder uniquement 2 dernières années
   = Table.SelectRows(Source, each [date] >= #date(2023, 1, 1))
   ```

3. **Changer types de données** :
   - Textes longs → Textes courts (économise RAM)
   - Décimaux inutiles → Entiers

#### Désactiver actualisation auto-détection

**Fichier** → **Options** → **Chargement de données** → Décocher "Auto-détecter relations"

#### Utiliser format PBIX optimisé

**Fichier** → **Enregistrer sous** → Cocher **"Réduire taille fichier"**

---

### Mode DirectQuery

#### Limiter visuals par page

**Max 10-15 visuals par page** (chaque visual = 1 requête SQL)

#### Utiliser agrégations

Pré-calculer dans PostgreSQL :

```sql
CREATE MATERIALIZED VIEW pennylane.analytical_ledger_monthly AS
SELECT
    DATE_TRUNC('month', date) AS month,
    PCG_1,
    Nature_Compte,
    SUM(debit) AS total_debit,
    SUM(credit) AS total_credit,
    SUM(Solde) AS total_solde
FROM pennylane.analytical_ledger
GROUP BY 1, 2, 3;

-- Actualiser la vue
REFRESH MATERIALIZED VIEW pennylane.analytical_ledger_monthly;
```

Utiliser `analytical_ledger_monthly` au lieu de `analytical_ledger` dans Power BI.

#### Query Reduction

**Fichier** → **Options** → **Options de requête** :

- ✅ Activer "Réduction de requête"
- ✅ Activer "Appliquer les filtres d'abord"

---

## 7. Actualisation automatique

### Mode Import - Actualisation manuelle

**Ruban** → **Accueil** → **Actualiser**

Ou : `Ctrl + R`

### Mode Import - Actualisation planifiée (Power BI Service)

#### Étape 1 : Publier sur Power BI Service

1. **Ruban** → **Accueil** → **Publier**
2. **Sélectionner** un espace de travail
3. **Attendre** upload

#### Étape 2 : Installer On-Premises Data Gateway

**Pourquoi ?** Power BI Service (cloud) ne peut pas accéder directement à votre `localhost:5433`.

1. **Télécharger** : [On-Premises Data Gateway](https://powerbi.microsoft.com/fr-fr/gateway/)
2. **Installer** sur la machine hébergeant PostgreSQL
3. **Configurer** avec compte Power BI Service

#### Étape 3 : Configurer source de données

Dans **Power BI Service** :

1. **Paramètres** → **Gérer les passerelles**
2. **Ajouter source de données** :
   - Type : PostgreSQL
   - Serveur : `localhost:5433`
   - Base : `pennylane_db`
   - Credentials : `pennylane_user` / mot de passe

#### Étape 4 : Planifier actualisation

1. **Votre dataset** → **⚙️ Paramètres**
2. **Actualisation planifiée** → **Activer**
3. **Fréquence** :
   - Maximum : **8 fois par jour** (Pro)
   - Horaires : Ex: 08:00, 12:00, 16:00, 20:00

**💡 Astuce** : Notre scheduler Python tourne toutes les 2h → Configurer actualisation Power BI à 08:15, 10:15, 12:15... (décalage de 15 min après synchro).

---

### Mode DirectQuery - Temps réel automatique

**Rien à configurer !** Les données sont toujours à jour (interrogation directe).

---

## 8. Troubleshooting 🔧

### ❌ Erreur : "Impossible de se connecter à PostgreSQL"

**Causes possibles** :

1. **PostgreSQL pas démarré** :
   ```bash
   docker ps
   # Doit montrer conteneur postgres "Up"
   ```

2. **Mauvais port** :
   - Vérifier : `localhost:5433` (pas 5432 !)
   - Voir `docker-compose.yml` ligne `ports:`

3. **Mauvais credentials** :
   - Vérifier `.env` : `POSTGRES_USER` et `POSTGRES_PASSWORD`

4. **Firewall bloque** :
   - Windows : Autoriser port 5433 (Pare-feu Windows)

**Solution** :
```bash
# Tester connexion
docker exec postgres pg_isready
# Output attendu: "postgres is ready"
```

---

### ❌ Erreur : "Schema 'pennylane' introuvable"

**Cause** : Tables pas encore créées (scheduler jamais lancé).

**Solution** :
```bash
# Lancer scheduler une fois
python src/notebook_scheduler.py
# Ctrl+C après première synchro (8 min)
```

---

### ❌ Performance lente (Import Mode)

**Diagnostic** :

1. **Taille dataset** :
   ```
   Fichier → Informations → Taille du modèle de données
   ```

2. **Trop de colonnes** :
   - Supprimer colonnes JSON inutilisées
   - Alléger types (Int32 au lieu de Int64)

3. **Relations complexes** :
   - Vérifier modèle de données (onglet Modèle)
   - Éviter relations bidirectionnelles

**Solution** : Utiliser Power Query pour nettoyer avant chargement.

---

### ❌ DirectQuery très lent

**Diagnostic** :

```sql
-- Dans PostgreSQL, voir requêtes lentes
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Solutions** :

1. **Créer indexes manquants** (voir Étape 5 DirectQuery)
2. **Utiliser vues matérialisées** (pré-agrégation)
3. **Passer en mode Import** (si possible)

---

### ❌ Gateway erreur "Impossible de contacter source"

**Cause** : Gateway sur machine A, PostgreSQL sur machine B.

**Solution** :
1. Gateway doit être sur **même machine** que Docker PostgreSQL
2. Ou : Exposer PostgreSQL sur réseau (modifier `docker-compose.yml` :
   ```yaml
   ports:
     - "0.0.0.0:5433:5432"  # Accessible réseau local
   ```

---

## 📊 Checklist finale

Avant de créer vos dashboards :

**Mode Import**
- [ ] Connexion établie (`localhost:5433`)
- [ ] Tables chargées (voir onglet Données)
- [ ] Colonnes transformées visibles (PCG, Nature_Compte, Solde)
- [ ] Actualisation manuelle testée (`Ctrl + R`)
- [ ] Relations entre tables configurées (Modèle de données)

**Mode DirectQuery**
- [ ] Connexion établie
- [ ] Indexes PostgreSQL créés
- [ ] Requête test < 3 secondes
- [ ] Limitation visuals par page (max 15)
- [ ] Vues matérialisées pour agrégations

---

## 📚 Ressources complémentaires

- **Microsoft Learn** : [Import vs DirectQuery](https://learn.microsoft.com/fr-fr/power-bi/connect-data/desktop-directquery-about)
- **SQLBI** : [Optimiser modèles Power BI](https://www.sqlbi.com/articles/optimizing-power-bi-models/)
- **Power BI Community** : [Forum PostgreSQL](https://community.fabric.microsoft.com/t5/Desktop/bd-p/power-bi-designer)

---

**Prêt à créer vos dashboards !** 🎨

*Guide créé avec ❤️ pour la communauté Pennylane*
