# 📓 Scheduler Orchestrateur de Notebooks

## 🎯 Philosophie du projet

Ce projet adopte une approche **"Notebooks First"** où :
- ✅ **Notebooks = Source unique de vérité**
- ✅ Modifications dans notebooks = Automatiquement appliquées
- ✅ Visualisation interactive des données
- ✅ Personnalisation totale selon vos besoins

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NOTEBOOKS JUPYTER                        │
│              (data/API Publique/*.ipynb)                    │
│                                                             │
│  🔧 Vous modifiez ici les transformations                  │
│  👁️  Vous visualisez les résultats en temps réel           │
│  ✅ Vous testez avant d'automatiser                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Exécution automatique toutes les 2h
                  ↓
┌─────────────────────────────────────────────────────────────┐
│            NOTEBOOK SCHEDULER (src/notebook_scheduler.py)   │
│                                                             │
│  🤖 Exécute vos notebooks modifiés                         │
│  💾 Sauvegarde résultats dans data/outputs/                │
│  📊 Exports vers PostgreSQL                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────┐
│              POSTGRESQL (localhost:5433)                    │
│                     Schema: pennylane                       │
│                                                             │
│  📊 12 tables synchronisées                                 │
│  🔄 Actualisées toutes les 2 heures                         │
│  🔌 Connectées à Power BI                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Workflow utilisateur

### 1️⃣ **Développement** (Notebooks Jupyter)

```bash
# Ouvrir Jupyter
jupyter notebook
```

**Exemple** : Ajouter une colonne personnalisée dans [`Import_analytical_ledger.ipynb`](data/API Publique/Import_analytical_ledger.ipynb)

```python
# Cellule existante : Transformations
df['PCG_1'] = df['plan_item_number'].astype(str).str[:1]
df['PCG_2'] = df['plan_item_number'].astype(str).str[:2]
df['PCG_3'] = df['plan_item_number'].astype(str).str[:3]

# ✨ VOTRE NOUVELLE COLONNE (exemple)
df['Ratio_Debit_Credit'] = df['debit'] / df['credit'].replace(0, 1)

# Visualiser immédiatement
df[['plan_item_number', 'PCG_1', 'Ratio_Debit_Credit']].head()
```

💡 **Avantage** : Vous voyez le résultat instantanément !

### 2️⃣ **Test** (Exécution manuelle)

Exécutez toutes les cellules du notebook :
- `Cell > Run All`
- Vérifiez que l'export PostgreSQL fonctionne
- Vérifiez les données dans pgAdmin

### 3️⃣ **Automatisation** (Scheduler)

```bash
# Lancer le scheduler
python src/notebook_scheduler.py
```

**Ce qu'il fait** :
- ✅ Exécute votre notebook modifié toutes les 2h
- ✅ Applique automatiquement vos transformations personnalisées
- ✅ Exporte vers PostgreSQL
- ✅ Sauvegarde l'historique dans `data/outputs/`

### 4️⃣ **Power BI** (Visualisation)

Connectez Power BI à PostgreSQL :
- **Host** : `localhost`
- **Port** : `5433`
- **Database** : `pennylane_db`
- **Schema** : `pennylane`

Vos colonnes personnalisées sont automatiquement disponibles ! 🎉

---

## 📋 Notebooks disponibles

### Tables API REST (Temps réel)
| Notebook | Table PostgreSQL | Description |
|----------|------------------|-------------|
| `Import_customers.ipynb` | `customers` | Clients |
| `Import_customer_invoices.ipynb` | `customer_invoices` | Factures clients |
| `Import_suppliers.ipynb` | `suppliers` | Fournisseurs |
| `Import_supplier_invoices.ipynb` | `supplier_invoices` | Factures fournisseurs |
| `Import_bank_transactions.ipynb` | `bank_transactions` | Transactions bancaires |

### Tables Redshift (Comptabilité)
| Notebook | Table PostgreSQL | Description |
|----------|------------------|-------------|
| `Import_analytical_ledger.ipynb` | `analytical_ledger` | Grand livre analytique ⭐ |
| `Import_general_ledger.ipynb` | `general_ledger` | Grand livre général |
| `Import_trial_balance.ipynb` | `trial_balance` | Balance générale |
| `Import_bank_accounts.ipynb` | `bank_accounts` | Comptes bancaires |
| `Import_fiscal_years.ipynb` | `fiscal_years` | Exercices fiscaux |
| `Import_tax_declarations.ipynb` | `tax_declarations` | Déclarations fiscales |
| `Import_vat_declarations.ipynb` | `vat_declarations` | Déclarations TVA |

---

## 🎨 Exemples de personnalisations

### Exemple 1 : Ajouter un indicateur métier

**Dans `Import_customer_invoices.ipynb`** :

```python
# Après l'extraction des données
df['Delai_Paiement'] = (pd.to_datetime(df['deadline']) - pd.to_datetime(df['date'])).dt.days
df['Retard'] = df['Delai_Paiement'] > 30
```

**Résultat** : Colonnes `Delai_Paiement` et `Retard` automatiquement disponibles dans PostgreSQL et Power BI !

### Exemple 2 : Classifier les comptes comptables

**Dans `Import_analytical_ledger.ipynb`** :

```python
# Classification personnalisée selon votre plan comptable
def classifier_compte(numero):
    if numero.startswith('6'):
        return 'Charges'
    elif numero.startswith('7'):
        return 'Produits'
    elif numero.startswith('4'):
        return 'Tiers'
    else:
        return 'Autre'

df['Categorie_Compte'] = df['plan_item_number'].astype(str).apply(classifier_compte)
```

### Exemple 3 : Calculer des KPIs

**Dans `Import_bank_transactions.ipynb`** :

```python
# Calcul solde cumulé
df = df.sort_values('date')
df['Solde_Cumule'] = df['amount'].cumsum()

# Identifier transactions importantes
df['Transaction_Importante'] = df['amount'].abs() > 1000
```

---

## 🔧 Configuration

### Modifier la fréquence d'exécution

**Fichier** : [`src/notebook_scheduler.py`](src/notebook_scheduler.py#L190)

```python
# Ligne 190 : Changer la fréquence
schedule.every(2).hours.do(self.run_sync)  # Actuel : 2 heures

# Exemples :
schedule.every(30).minutes.do(self.run_sync)  # Toutes les 30 minutes
schedule.every(1).hours.do(self.run_sync)     # Toutes les heures
schedule.every().day.at("08:00").do(self.run_sync)  # Tous les jours à 8h
```

### Ajouter/Retirer des notebooks

**Fichier** : [`src/notebook_scheduler.py`](src/notebook_scheduler.py#L35)

```python
# Ligne 35 : Liste des notebooks
self.notebooks = [
    {
        'name': 'ma_table_custom',
        'notebook': 'Import_ma_table.ipynb',
        'description': 'Ma table personnalisée'
    },
    # ... autres notebooks
]
```

---

## 📊 Historique d'exécution

Chaque exécution crée un notebook de sortie :

```
data/outputs/
├── analytical_ledger_20251015_123045.ipynb
├── analytical_ledger_20251015_143045.ipynb  ← Dernière exécution
├── customers_20251015_123045.ipynb
└── ...
```

**Utilité** :
- ✅ Audit : Voir exactement ce qui a été exécuté
- ✅ Debug : Identifier erreurs dans l'historique
- ✅ Comparaison : Voir l'évolution des données

---

## 🆚 Comparaison avec l'ancien scheduler

| Critère | Ancien Scheduler<br>(`unified_scheduler.py`) | Nouveau Scheduler<br>(`notebook_scheduler.py`) |
|---------|----------------------------------------------|-----------------------------------------------|
| **Source de vérité** | Code Python dupliqué | Notebooks Jupyter |
| **Modifications** | Modifier 2 endroits (notebook + py) | ✅ Modifier 1 seul endroit (notebook) |
| **Visualisation** | ❌ Pas de visualisation | ✅ Visualisation interactive |
| **Personnalisation** | Compétences Python requises | ✅ Utilisateurs non-devs OK |
| **Historique** | Logs texte uniquement | ✅ Notebooks exécutés complets |
| **Open-source** | Difficile à forker/adapter | ✅ Facile à personnaliser |
| **Performance** | ~8 min | ~10-12 min (léger overhead) |

---

## ❓ FAQ

### Puis-je utiliser les deux schedulers en parallèle ?

Non, ils feraient doublon. Choisissez l'un ou l'autre :
- **`notebook_scheduler.py`** ⭐ **Recommandé** : Flexibilité maximale
- **`unified_scheduler.py`** : Performance optimale mais rigide

### Que se passe-t-il en cas d'erreur dans un notebook ?

Le scheduler :
1. ✅ Continue avec les notebooks suivants (pas de blocage)
2. ✅ Log l'erreur dans `logs/notebook_scheduler.log`
3. ✅ Sauvegarde le notebook avec erreur dans `data/outputs/`
4. ✅ Affiche clairement le bilan (X succès, Y erreurs)

### Comment voir les logs en temps réel ?

```bash
# Windows
Get-Content logs\notebook_scheduler.log -Wait

# Linux/Mac
tail -f logs/notebook_scheduler.log
```

### Puis-je exécuter un seul notebook manuellement ?

Oui ! Deux options :

**Option 1** : Jupyter (manuel)
```bash
jupyter notebook
# Ouvrir le notebook → Run All
```

**Option 2** : Papermill (CLI)
```bash
papermill "data/API Publique/Import_analytical_ledger.ipynb" "data/outputs/test.ipynb"
```

---

## 🎯 Bonnes pratiques

### ✅ DO
- Testez vos modifications dans Jupyter avant d'automatiser
- Ajoutez des affichages (`display(df.head())`) pour visualiser
- Commentez vos transformations personnalisées
- Commitez régulièrement vos notebooks sur Git

### ❌ DON'T
- Ne pas modifier `notebook_scheduler.py` directement (sauf config)
- Ne pas supprimer les cellules d'export PostgreSQL
- Ne pas renommer les notebooks sans mettre à jour la config

---

## 🚀 Quick Start

```bash
# 1. Cloner le repo
git clone https://github.com/votre-username/Penny.git
cd Penny

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Configurer .env
cp .env.example .env
# Éditer .env avec vos credentials

# 4. Démarrer PostgreSQL
docker-compose up -d

# 5. Tester un notebook manuellement
jupyter notebook
# Ouvrir Import_analytical_ledger.ipynb → Run All

# 6. Lancer l'automatisation
python src/notebook_scheduler.py
```

**🎉 C'est tout ! Vos notebooks s'exécutent maintenant automatiquement toutes les 2h !**

---

## 🤝 Contribution

Ce projet est open-source. Vous pouvez :
- Forker et adapter à vos besoins
- Partager vos notebooks personnalisés
- Soumettre des améliorations via Pull Requests

---

## 📧 Support

- Documentation : [README.md](README.md)
- Issues : [GitHub Issues](https://github.com/votre-username/Penny/issues)
- Communauté Pennylane : [community.pennylane.com](https://community.pennylane.com)

---

**Créé avec ❤️ pour la communauté Pennylane**
