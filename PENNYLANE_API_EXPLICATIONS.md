# 🔌 Comprendre les API Pennylane

## 🎯 Vue d'ensemble

Pennylane propose **2 méthodes d'accès** aux données, chacune avec ses particularités :

1. **API REST** (temps réel) → Pour la gestion commerciale
2. **Data Sharing** (cache 2h) → Pour la comptabilité

---

## 📊 Les 2 types d'accès Pennylane

### 1️⃣ API REST - Temps réel (5 tables)

**C'est quoi ?**
- API HTTP classique avec des endpoints REST
- Accès **direct** à la base de données en production

**Tables disponibles** :
- ✅ **Clients** (`customers`)
- ✅ **Fournisseurs** (`suppliers`)
- ✅ **Factures clients** (`customer_invoices`)
- ✅ **Factures fournisseurs** (`supplier_invoices`)
- ✅ **Comptes bancaires** (`bank_accounts`)

**Caractéristiques** :
- ⚡ **Temps réel** : Les données sont à jour instantanément
- 🚀 **Rapide** : Réponse en quelques millisecondes
- 📊 **Gestion commerciale** : Clients, factures en cours, etc.
- 🔑 **Token API** : `PENNYLANE_API_TOKEN`
- 🔒 **Rate limit** : 5 requêtes/seconde (300/minute)

**Exemple d'utilisation** :
```python
# Récupérer la liste des clients
GET https://app.pennylane.com/api/v1/customers
Authorization: Bearer YOUR_API_TOKEN
```

**Pourquoi temps réel ?**
→ Ces données changent fréquemment (nouvelles factures, nouveaux clients) et les utilisateurs ont besoin de les voir **immédiatement**.

---

### 2️⃣ Data Sharing (Redshift) - Cache 2 heures (7 tables)

**C'est quoi ?**
- Accès **SQL direct** à un Data Warehouse (Redshift)
- Les données sont **copiées** depuis la production toutes les 2 heures

**Tables disponibles** :
- ✅ **Grand livre** (`analytical_ledger`)
- ✅ **Grand livre général** (`general_ledger`)
- ✅ **Balance générale** (`trial_balance`)
- ✅ **Exercices fiscaux** (`fiscal_years`)
- ✅ **Déclarations TVA** (`vat_declarations`)
- ✅ **Déclarations fiscales** (`tax_declarations`)
- ✅ **Transactions bancaires** (`bank_transactions`)

**Caractéristiques** :
- 🕐 **Cache 2 heures** : Les données ne sont pas en temps réel
- 📚 **Données comptables** : Grand livre, balance, TVA
- 🔍 **Grosses volumétries** : Des millions de lignes
- 🔑 **Data Sharing Key** : `PENNYLANE_DATA_SHARING_KEY`
- 🗄️ **Redshift** : Base de données SQL optimisée pour l'analytique

**Exemple d'utilisation** :
```python
import psycopg2

# Connexion à Redshift
conn = psycopg2.connect(
    host='pennylane-external.csqwamh5pldr.eu-west-1.redshift.amazonaws.com',
    port=5439,
    database='prod',
    user='u_289572',
    password=PENNYLANE_DATA_SHARING_KEY
)

# Requête SQL
SELECT * FROM pennylane.analytical_ledger
WHERE date >= '2025-01-01'
```

**Pourquoi un cache de 2 heures ?**
→ Pour des raisons de **performance** et de **coût**.

---

## 🤔 Pourquoi cette différence ?

### Problématique technique

**1. Volume de données**

| Type | Volumétrie typique | Fréquence de consultation |
|------|-------------------|---------------------------|
| **Clients** | Centaines | Plusieurs fois par jour |
| **Grand livre** | **Millions de lignes** | Quelques fois par semaine |

**2. Complexité des requêtes**

**API REST (temps réel)** :
```sql
-- Simple : récupérer un client
SELECT * FROM customers WHERE id = 123
```
→ Requête rapide, base de données peut gérer en temps réel.

**Data Sharing (cache 2h)** :
```sql
-- Complexe : balance comptable sur 5 ans
SELECT
    account_number,
    SUM(debit) - SUM(credit) as balance
FROM analytical_ledger
WHERE date BETWEEN '2020-01-01' AND '2025-12-31'
GROUP BY account_number
HAVING balance != 0
ORDER BY account_number
```
→ Requête lourde, impossible en temps réel sans ralentir toute l'application.

---

## 💡 La stratégie de Pennylane

### Pourquoi 2 systèmes ?

**API REST (temps réel)** → Pour les **opérations courantes**
- Créer une facture
- Ajouter un client
- Consulter un paiement
→ **Impact utilisateur** : L'utilisateur attend une réponse immédiate

**Data Sharing (cache 2h)** → Pour l'**analyse et le reporting**
- Balance comptable
- Déclarations TVA
- Grand livre sur plusieurs années
→ **Impact utilisateur** : L'utilisateur fait du reporting, 2h de décalage est acceptable

---

## 📈 Architecture technique

```
┌─────────────────────────────────────────────────────────────┐
│                    PENNYLANE PRODUCTION                      │
│                                                              │
│  ┌────────────────────┐         ┌───────────────────────┐  │
│  │  Base de données   │         │   Base de données     │  │
│  │  Opérationnelle    │         │   Comptable           │  │
│  │                    │         │                       │  │
│  │  - Clients         │         │  - Grand livre        │  │
│  │  - Factures        │         │  - Balance            │  │
│  │  - Fournisseurs    │         │  - Déclarations       │  │
│  └────────┬───────────┘         └──────────┬────────────┘  │
│           │                                 │               │
└───────────┼─────────────────────────────────┼───────────────┘
            │                                 │
            │ Temps réel                      │ Copie toutes les 2h
            │                                 │
            ▼                                 ▼
    ┌───────────────┐                ┌─────────────────┐
    │   API REST    │                │  Data Warehouse │
    │               │                │   (Redshift)    │
    │  5 req/sec    │                │                 │
    │               │                │  Cache 2h       │
    └───────────────┘                └─────────────────┘
            │                                 │
            │                                 │
            ▼                                 ▼
    ┌───────────────────────────────────────────────────┐
    │           VOTRE ETL PENNY                         │
    │                                                   │
    │  - Synchronisation toutes les 2h                 │
    │  - 5 tables API REST (temps réel)                │
    │  - 7 tables Redshift (cache 2h)                  │
    │  - Export vers PostgreSQL                        │
    └───────────────────────────────────────────────────┘
```

---

## ⏱️ Fréquence de mise à jour

### Tableau récapitulatif

| Source | Tables | Fraîcheur | Fréquence synchro Penny |
|--------|--------|-----------|------------------------|
| **API REST** | Clients, Fournisseurs, Factures, Comptes | **Temps réel** | Toutes les 2h |
| **Redshift** | Grand livre, Balance, TVA, Transactions | **Cache 2h** | Toutes les 2h |

**Résultat pour vous** :
- ✅ Vos données de gestion sont à jour toutes les 2h
- ✅ Vos données comptables sont à jour avec un décalage de 2-4h maximum
  - 2h (cache Pennylane) + 2h (synchro Penny) = 4h max

---

## 🎯 Impact pratique

### Cas d'usage : Période de clôture comptable

**Scénario** : Vous êtes en clôture de mois, vous saisissez des écritures dans Pennylane.

**Timeline** :
```
10h00 → Vous saisissez une écriture dans Pennylane
10h00 → Écriture visible dans Pennylane (interface web)
12h00 → Pennylane copie les données vers Redshift (cache 2h)
12h00 → Écriture disponible via Data Sharing
14h00 → Votre ETL Penny synchronise (toutes les 2h)
14h00 → Écriture visible dans Power BI
```

**Délai maximum** : 4 heures entre la saisie et Power BI

---

### Pourquoi c'est acceptable ?

**En compta, contrairement à la gestion** :
- ✅ On ne fait pas 50 écritures par heure
- ✅ On travaille sur des périodes (mois, trimestre)
- ✅ On a besoin de **cohérence** plus que de temps réel
- ✅ Le reporting est fait en fin de journée/semaine/mois

**Exemple** :
- ❌ **Mauvais** pour : Vérifier si un paiement client vient d'arriver (→ utiliser l'interface Pennylane)
- ✅ **Bon** pour : Analyser tous les paiements du mois dernier (→ utiliser Power BI avec Penny)

---

## 🔄 Optimisation avec Penny

### Ce que fait Penny

**Sans Penny** :
- Power BI interroge directement Pennylane
- Temps de chargement : **30-60 minutes**
- Impossible de faire des analyses complexes

**Avec Penny** :
1. ✅ Penny synchronise toutes les 2h automatiquement
2. ✅ Les données sont **pré-traitées** et stockées dans PostgreSQL
3. ✅ Power BI interroge PostgreSQL (local)
4. ✅ Temps de chargement : **2-5 minutes**

**Bénéfice** :
- 🚀 **12x plus rapide** (de 60 min à 5 min)
- 📊 Possibilité de faire des analyses complexes
- 🔄 Données toujours synchronisées automatiquement

---

## 🔑 Les 2 tokens nécessaires

### Dans votre fichier .env

```env
# API REST (temps réel) - 5 tables
PENNYLANE_API_TOKEN=pk_live_abc123...

# Data Sharing (cache 2h) - 7 tables
PENNYLANE_DATA_SHARING_KEY=dsk_xyz789...
```

**Important** : Ce sont **2 tokens différents** !

---

## 📚 Où trouver ces tokens ?

### 1. API REST Token

1. Connectez-vous à Pennylane
2. **Paramètres** → **Développeurs** → **API**
3. Cliquez sur **"Créer un token"**
4. Copiez le token (`pk_live_...`)

### 2. Data Sharing Key

1. **Paramètres** → **Développeurs** → **Data Sharing**
2. Copiez le **"Data Sharing Key"** (`dsk_...`)

---

## 🎓 En résumé

| Aspect | API REST | Data Sharing (Redshift) |
|--------|----------|------------------------|
| **Type de données** | Gestion commerciale | Comptabilité |
| **Fraîcheur** | ⚡ Temps réel | 🕐 Cache 2h |
| **Tables** | 5 tables | 7 tables |
| **Volumétrie** | Faible (milliers) | Élevée (millions) |
| **Token** | `PENNYLANE_API_TOKEN` | `PENNYLANE_DATA_SHARING_KEY` |
| **Protocole** | HTTP REST | SQL (Redshift) |
| **Use case** | Opérations courantes | Reporting & Analytics |

---

## 💡 Conseil pratique

**Quand actualiser vos données ?**

- 🔄 **Toutes les 2h** (recommandé) : Bon compromis entre fraîcheur et charge serveur
- ⚡ **Toutes les 10 min** : Si vous êtes en pleine saisie comptable intensive
- 🌙 **Une fois par nuit** : Si vous faites juste du reporting mensuel

**Comment changer la fréquence ?**

Voir le [GUIDE_AUTOMATION.md](GUIDE_AUTOMATION.md) section "Puis-je changer la fréquence d'actualisation ?"

---

## ❓ FAQ

### "Pourquoi mes données comptables ne sont pas en temps réel ?"

**Réponse** : C'est une limitation de Pennylane. Le cache de 2h est imposé par Pennylane pour des raisons de performance. Vos données ne peuvent pas être plus fraîches que ça.

### "Puis-je contourner le cache de 2h ?"

**Réponse** : Non, c'est impossible. C'est Pennylane qui contrôle ça. Même si vous synchronisez toutes les 5 minutes, vous aurez toujours les mêmes données pendant 2 heures.

### "Les données de gestion sont-elles vraiment en temps réel ?"

**Réponse** : Oui, l'API REST donne des données temps réel. Mais **votre synchro Penny** tourne toutes les 2h, donc dans Power BI vous aurez un décalage maximum de 2h.

### "Comment avoir du temps réel dans Power BI ?"

**Réponse** :
1. Synchronisez plus souvent (toutes les 10 min au lieu de 2h)
2. Ou utilisez DirectQuery dans Power BI (mais ce sera plus lent)

---

## 🔗 Ressources

- **Documentation officielle Pennylane API** : [https://pennylane.readme.io/](https://pennylane.readme.io/)
- **Guide automatisation Penny** : [GUIDE_AUTOMATION.md](GUIDE_AUTOMATION.md)
- **Architecture du projet** : [README.md](README.md)

---

**Auteur** : Yves Cloarec
**Projet** : [Penny - ETL Open Source](https://github.com/yves34690/Penny)
**Date** : Octobre 2025
