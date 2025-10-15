# ⚖️ Quel scheduler choisir ?

Deux schedulers sont disponibles dans ce projet. Voici comment choisir :

---

## 🆚 Comparaison détaillée

| Critère | **Notebook Scheduler**<br>`src/notebook_scheduler.py` | **Unified Scheduler**<br>`src/unified_scheduler.py` |
|---------|------------------------------------------------------|---------------------------------------------------|
| **🎯 Philosophie** | Notebooks = Source de vérité | Code Python = Source de vérité |
| **👥 Public cible** | ✅ Tous (y compris non-devs) | Développeurs Python |
| **🔧 Personnalisation** | ⭐⭐⭐⭐⭐ Très facile (notebooks) | ⭐⭐⭐ Moyen (code Python) |
| **👁️ Visualisation** | ✅ Interactive dans Jupyter | ❌ Logs texte uniquement |
| **📊 Historique** | ✅ Notebooks exécutés complets | Logs texte |
| **⚡ Performance** | ~10-12 min | ⭐ ~8 min (plus rapide) |
| **🔄 Maintenance** | ⭐⭐⭐⭐⭐ Facile (1 seul endroit) | ⭐⭐ Difficile (2 endroits) |
| **🌍 Open-source** | ⭐⭐⭐⭐⭐ Facilement forkable | ⭐⭐⭐ Nécessite compétences Python |
| **📦 Dépendances** | +3 (papermill, nbformat, nbconvert) | Minimales |
| **💾 Stockage** | Plus élevé (notebooks outputs) | Minimal (logs uniquement) |

---

## 🎯 Recommandations par profil

### ✅ **Notebook Scheduler** - RECOMMANDÉ pour :

1. **Expert-comptable / DAF sans compétences Python**
   - Vous voulez personnaliser les données
   - Vous préférez visualiser dans Excel/Jupyter
   - Vous n'êtes pas à l'aise avec le code Python

2. **Projet open-source destiné à la communauté**
   - Vous voulez que d'autres puissent facilement adapter
   - Vous voulez maximiser la réutilisabilité
   - Vous acceptez un léger overhead de performance (2-3 min)

3. **Développement actif / Itératif**
   - Vous testez souvent de nouvelles transformations
   - Vous voulez voir les résultats immédiatement
   - Vous ajoutez régulièrement des colonnes/calculs

4. **Audit et traçabilité**
   - Vous avez besoin d'historique détaillé
   - Vous voulez voir exactement ce qui a été exécuté
   - Vous devez prouver vos calculs

**👉 C'est le choix du créateur de ce projet pour maximiser l'adoption communautaire**

---

### ✅ **Unified Scheduler** - RECOMMANDÉ pour :

1. **Environnement de production stable**
   - Configuration finalisée, peu de changements
   - Performance critique (8 min vs 12 min)
   - Ressources limitées (CPU/RAM/Stockage)

2. **Développeur Python expérimenté**
   - Vous êtes à l'aise avec SQLAlchemy/Pandas
   - Vous préférez tout contrôler en code
   - Vous n'avez pas besoin de visualisation interactive

3. **Infrastructure sans interface graphique**
   - Serveur headless sans Jupyter
   - Déploiement Docker en production
   - Automatisation CI/CD

4. **Données sensibles**
   - Vous ne voulez pas sauvegarder les notebooks outputs
   - Stockage minimal requis
   - Logs texte suffisants

---

## 📋 Décision rapide

### Posez-vous ces questions :

**Q1 : Les utilisateurs finaux vont-ils modifier les transformations ?**
- ✅ **Oui** → Notebook Scheduler
- ❌ **Non** → Unified Scheduler

**Q2 : Avez-vous besoin de visualisation interactive ?**
- ✅ **Oui** → Notebook Scheduler
- ❌ **Non** → Unified Scheduler

**Q3 : Le projet est-il destiné à être partagé/forké ?**
- ✅ **Oui** → Notebook Scheduler
- ❌ **Non** → Unified Scheduler

**Q4 : La performance est-elle critique (différence 2-3 min) ?**
- ✅ **Oui** → Unified Scheduler
- ❌ **Non** → Notebook Scheduler

---

## 🚀 Comment démarrer

### Option 1 : Notebook Scheduler (Recommandé ⭐)

```bash
# 1. Arrêter l'ancien scheduler si actif
# Ctrl+C dans le terminal où il tourne

# 2. Lancer le notebook scheduler
python src/notebook_scheduler.py
```

**Voir documentation complète** : [README_NOTEBOOK_SCHEDULER.md](README_NOTEBOOK_SCHEDULER.md)

---

### Option 2 : Unified Scheduler

```bash
# 1. Arrêter le notebook scheduler si actif
# Ctrl+C

# 2. Lancer l'unified scheduler
python src/unified_scheduler.py
```

**Note** : Le fichier `unified_scheduler.py` a été supprimé dans cette version simplifiée du projet. Si vous souhaitez l'utiliser, consultez les anciennes versions du dépôt GitHub.

**Pourquoi recommandons-nous le Notebook Scheduler ?** : Plus facile à maintenir, accessible aux non-développeurs, et permet de modifier les transformations sans toucher au code Python.

---

## ⚠️ Attention : Ne pas utiliser les deux en parallèle !

**Problèmes si les deux tournent ensemble** :
- ❌ Doublon de synchronisations (charge API/Redshift)
- ❌ Conflits d'écriture PostgreSQL
- ❌ Logs confus
- ❌ Gaspillage de ressources

**Règle d'or** : 1 seul scheduler actif à la fois !

---

## 🔄 Migrer d'un scheduler à l'autre

### De Unified → Notebook

1. Arrêter `unified_scheduler.py` (Ctrl+C)
2. Vérifier que vos notebooks contiennent les mêmes transformations
3. Tester un notebook manuellement (`jupyter notebook`)
4. Lancer `notebook_scheduler.py`

**Note** : Les tables PostgreSQL existantes seront écrasées (mode `replace`)

---

### De Notebook → Unified

1. Arrêter `notebook_scheduler.py` (Ctrl+C)
2. Copier vos transformations personnalisées depuis notebooks vers `unified_scheduler.py` fonction `_transform_analytical_ledger()`
3. Lancer `unified_scheduler.py`

**Attention** : Nécessite compétences Python pour adapter les transformations !

---

## 📊 Tableau de synthèse : Cas d'usage

| Cas d'usage | Scheduler recommandé |
|-------------|---------------------|
| Projet GitHub public destiné à la communauté | ⭐ **Notebook** |
| Expert-comptable souhaitant personnaliser | ⭐ **Notebook** |
| Data analyst explorant les données | ⭐ **Notebook** |
| Développement actif avec tests fréquents | ⭐ **Notebook** |
| Production stable sans changements | **Unified** |
| Serveur headless sans interface graphique | **Unified** |
| Performance critique (volumes énormes) | **Unified** |
| Stockage limité | **Unified** |

---

## 💡 Conseil du créateur

> **Pour ce projet open-source destiné à la communauté Pennylane, j'ai choisi le Notebook Scheduler.**
>
> **Raison** : Maximiser l'accessibilité et la réutilisabilité. Les utilisateurs peuvent visualiser, comprendre et personnaliser facilement sans compétences Python avancées.
>
> L'overhead de 2-3 minutes par synchronisation est négligeable comparé à la flexibilité offerte.

---

## ❓ Questions fréquentes

### Puis-je basculer entre les deux selon les jours ?

Techniquement oui, mais **non recommandé**. Choisissez-en un et tenez-vous-y pour :
- Cohérence des logs
- Simplicité de maintenance
- Éviter les confusions

### Le Notebook Scheduler est-il vraiment plus lent ?

Oui, ~2-3 minutes de plus dû à :
- Démarrage kernel Jupyter (x12 notebooks)
- Parsing/Sauvegarde des notebooks outputs

**Mais** : Sur une synchro toutes les 2h, c'est 0.02% du temps total → **Négligeable !**

### Puis-je créer un scheduler hybride ?

Oui, techniquement possible :
- Notebooks pour tables avec transformations complexes
- Unified pour tables simples sans transformations

**Mais** : Complexité accrue, non recommandé sauf besoin très spécifique.

---

## 🎯 TL;DR : Quel scheduler pour vous ?

```
┌─────────────────────────────────────────────────────────┐
│  Vous voulez partager votre projet sur GitHub ?        │
│  → NOTEBOOK SCHEDULER                                   │
│                                                         │
│  Vous avez un setup perso stabilisé sans partage ?     │
│  → UNIFIED SCHEDULER                                    │
└─────────────────────────────────────────────────────────┘
```

---

**Besoin d'aide pour choisir ?** Ouvrez une issue sur GitHub ! 🤝
