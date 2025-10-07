# Mission d'accompagnement Claude - Projet Penny

## 🎯 Objectif de la mission

Accompagner la création d'un projet ETL open-source permettant d'extraire les données Pennylane, de les traiter et de les rendre disponibles pour Power BI avec des performances optimales et une fréquence de rafraîchissement élevée.

## 📋 Problématiques initiales

### 1. Performance Power BI
- **Constat** : Temps de rafraîchissement de 30-60 minutes
- **Cause** : Transformations lourdes dans Power Query sur des millions de lignes
- **Solution proposée** : Déporter les transformations en Python/PostgreSQL

### 2. Fréquence de rafraîchissement
- **Constat** : API Pennylane avec cache de 2 heures
- **Besoin** : Données quasi temps-réel pendant les périodes de révision comptable intensive
- **Solution proposée** : Scheduler Python avec rafraîchissement toutes les 10 minutes

## 🏗️ Architecture développée

```
Pennylane API/Redshift
        ↓
    Python ETL (toutes les 10 min)
        ↓
    PostgreSQL (données traitées)
        ↓
    Power BI / Jupyter
```

## 📂 Structure du projet créée

```
Penny/
├── .env                          # Credentials (non commité)
├── .env.example                  # Template credentials
├── docker-compose.yml            # PostgreSQL + pgAdmin
├── requirements.txt              # Dépendances Python
├── config.json                   # Configuration endpoints
├── src/
│   ├── config_loader.py         # Chargement configuration
│   ├── pennylane_api.py         # Client API avec rate limiting
│   ├── database.py              # Opérations PostgreSQL
│   ├── transformations.py       # Transformations données
│   ├── main.py                  # Orchestration ETL
│   └── scheduler.py             # Automatisation 10 min
├── data/
│   └── import_list_table.ipynb  # Exploration Redshift
├── tests/
│   └── test_redshift.py         # Test connexion Redshift
├── docs/                        # Documentation MkDocs
└── .github/workflows/           # CI/CD GitHub Actions
```

## 🚀 Étapes de réalisation

### Phase 1 : Recherche et architecture (Messages 1-15)
1. ✅ Recherche documentation API Pennylane
2. ✅ Analyse problèmes performance Power BI
3. ✅ Proposition architecture ETL complète
4. ✅ Validation des besoins utilisateur (volume, fréquence, transformations)
5. ✅ Identification contraintes techniques (rate limiting API)

### Phase 2 : Développement core ETL (Messages 16-40)
1. ✅ Configuration sécurisée avec `.env` et `.env.example`
2. ✅ Setup Docker PostgreSQL + pgAdmin
3. ✅ Client API avec rate limiting (4.5 req/sec)
4. ✅ Gestion pagination API
5. ✅ Module base de données avec batch loading
6. ✅ Orchestration ETL (mode full/incremental)
7. ✅ Scheduler automatique 10 minutes
8. ✅ Documentation utilisateur complète

### Phase 3 : GitHub et déploiement (Messages 41-55)
1. ✅ Création repository GitHub "Penny"
2. ✅ Documentation MkDocs avec 8 pages
3. ✅ GitHub Actions CI/CD
4. ✅ Déploiement GitHub Pages
5. ✅ Badges professionnels README
6. ✅ Guide utilisateur évolutif

### Phase 4 : Setup PostgreSQL (Messages 56-65)
1. ✅ Configuration `.env` avec credentials Pennylane
2. ✅ Résolution conflit port (5432 → 5433)
3. ✅ Lancement Docker Compose
4. ✅ Vérification création base et schémas
5. ✅ Validation PostgreSQL opérationnel

### Phase 5 : Clarification accès Pennylane (Messages 66-75)
1. ✅ Identification 2 méthodes d'accès distinctes :
   - **Data Sharing** : Accès SQL direct au Data Warehouse Redshift
   - **API REST** : API avec scopes et tokens développeurs
2. ✅ Séparation tokens dans `.env` :
   - `PENNYLANE_DATA_SHARING_KEY` pour Redshift
   - `PENNYLANE_API_TOKEN` pour REST API
3. ✅ Test connexion Redshift réussi
4. ✅ Validation accès Data Warehouse fonctionnel

### Phase 6 : Jupyter Notebooks (Messages 76-83)
1. ✅ Création `import_list_table.ipynb`
2. ✅ **Apprentissage structure notebook** : alternance markdown/code/display
3. ✅ Code exploration tables Redshift
4. ✅ Configuration environnement Python 3.12.10
5. ✅ Installation pyarrow
6. ✅ Correction requête SQL (`information_schema.tables`)

## 📚 Apprentissages clés

### 1. Double accès Pennylane
**Découverte importante** : Pennylane propose 2 méthodes d'accès différentes :
- **Redshift Data Sharing** : Accès direct SQL au Data Warehouse (port 5439)
- **API REST** : API HTTP avec rate limiting et pagination

**Impact** : Nécessité de séparer les deux tokens et de clarifier l'usage selon le besoin.

### 2. Structure Jupyter Notebooks
**Feedback utilisateur critique** :
> "l'intérêt de jupyter notebook c'est que je puisse visualiser. et donc en fonction retraiter. il faut donc qu'il y ait plusieurs print en sortie afin de visualiser chaque étape."

**Apprentissage** :
- ❌ **Erreur initiale** : Regrouper tout le code ensemble puis tous les affichages
- ✅ **Bonne pratique** : Alterner Markdown → Code → Display → Markdown → Code → Display
- **Raison** : Permet une visualisation et un ajustement progressif à chaque étape

### 3. Permissions Redshift
**Problème rencontré** : `permission denied for relation pg_tables`

**Apprentissage** :
- Les vues système PostgreSQL (`pg_tables`, `pg_views`) ne sont pas toujours accessibles sur Redshift
- **Solution** : Utiliser `information_schema.tables` qui est accessible par défaut

### 4. Mots réservés SQL
**Erreur** : `syntax error at or near "table"`

**Apprentissage** :
- `table` est un mot réservé en SQL
- **Solutions** :
  1. Renommer la colonne (`table` → `table_name`)
  2. Entourer de guillemets doubles (`"table"`)

### 5. Gestion ports Docker sur Windows
**Problème** : Port 5432 déjà utilisé par un autre conteneur PostgreSQL

**Apprentissage** :
- Vérifier les ports utilisés avec `docker ps`
- Configurer port alternatif via variables d'environnement
- Utiliser `.env` pour rendre la configuration flexible

### 6. Encodage Windows et emojis
**Problème** : `UnicodeEncodeError: 'charmap' codec can't encode character`

**Apprentissage** :
- Console Windows ne supporte pas tous les emojis
- **Solution** : Remplacer par indicateurs texte (`[OK]`, `[ERREUR]`)

### 7. Installation packages Jupyter
**Avertissement** : `Defaulting to user installation because normal site-packages is not writeable`

**Apprentissage** :
- Installation au niveau utilisateur est normale sur Windows
- Nécessite redémarrage du kernel Jupyter pour prise en compte
- Utiliser `Note: you may need to restart the kernel` comme signal

## 🔄 Workflow de travail établi

### Développement ETL automatisé (original)
```
1. Extraction API/Redshift
2. Transformations Python
3. Chargement PostgreSQL
4. Connexion Power BI
```

### Workflow utilisateur final (découvert)
```
1. Extraction manuelle via Jupyter Notebooks
2. Visualisation progressive des données
3. Retraitement itératif selon résultats
4. Transformations adaptées aux besoins spécifiques
```

**Impact** : L'utilisateur préfère contrôler manuellement l'extraction via notebooks plutôt qu'utiliser l'ETL automatisé. Le projet devient une **boîte à outils** plutôt qu'un pipeline automatisé.

## 🛠️ Technologies utilisées

- **Python 3.12** : Langage principal
- **PostgreSQL 15** : Base de données (via Docker)
- **Redshift** : Data Warehouse Pennylane
- **Jupyter Notebooks** : Exploration et transformation interactive
- **Docker Compose** : Orchestration conteneurs
- **python-dotenv** : Gestion credentials
- **psycopg2** : Connexion PostgreSQL/Redshift
- **pandas** : Manipulation données
- **pyarrow** : Performance pandas
- **MkDocs Material** : Documentation
- **GitHub Actions** : CI/CD

## 📊 Décisions techniques clés

| Décision | Raison |
|----------|--------|
| PostgreSQL 15 au lieu de 16 | Image déjà en cache localement |
| Port 5433 au lieu de 5432 | Éviter conflit avec PostgreSQL existant |
| Rate limiting à 4.5 req/sec | Marge de sécurité sous limite API (5 req/sec) |
| Batch size 1000 lignes | Compromis performance/mémoire |
| 2 tokens séparés | Clarifier usage Redshift vs API REST |
| `information_schema.tables` | Permissions Redshift limitées |
| Python 3.12.10 Global Env | Cohérence avec installation système |

## 🎓 Méthodologie d'accompagnement

### Principes suivis
1. **Dialogue avant action** : Clarifier besoins avant développer
2. **Itératif** : Ajuster selon retours utilisateur
3. **Documentation complète** : Projet partageable et réutilisable
4. **Sécurité** : `.env` non commité, `.env.example` fourni
5. **Standards professionnels** : CI/CD, tests, documentation

### Adaptation au feedback
- **Modification structure notebooks** suite retour utilisateur
- **Séparation tokens** après clarification usage
- **Changement port PostgreSQL** selon infrastructure existante
- **Passage d'ETL automatisé à boîte à outils** selon workflow préféré

## 🔮 Perspectives futures

### Court terme
- [ ] Finaliser exploration tables Redshift dans notebook
- [ ] Créer notebooks supplémentaires pour autres endpoints
- [ ] Documenter requêtes SQL réutilisables

### Moyen terme
- [ ] Partage public du repository GitHub
- [ ] Contributions communautaires possibles
- [ ] Enrichissement documentation avec cas d'usage

### Long terme
- [ ] Éventuellement réactiver ETL automatisé si besoin
- [ ] Intégration d'autres sources comptables
- [ ] Dashboards Power BI préconstruits

## 📝 Notes importantes

### Variables d'environnement sensibles
```env
PENNYLANE_DATA_SHARING_KEY=***  # Redshift access
PENNYLANE_API_TOKEN=***         # REST API access
POSTGRES_PASSWORD=***           # PostgreSQL password
```

**⚠️ Ne jamais commiter `.env` sur GitHub**

### Commandes essentielles

```bash
# Démarrer PostgreSQL
docker-compose up -d

# Installer dépendances Python
pip install -r requirements.txt

# Tester connexion Redshift
python tests/test_redshift.py

# Lancer Jupyter
jupyter notebook
```

## 🤝 Collaboration

Le projet est conçu pour être **open-source et partageable**. Toute contribution future devra :
- Respecter la structure établie
- Documenter les changements
- Tester avant commit
- Suivre les standards du projet

---

**Date de création** : 2025-10-07
**Dernière mise à jour** : 2025-10-07
**Statut** : En développement actif
