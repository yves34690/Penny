# Dépannage

Guide de résolution des problèmes courants.

## Erreurs de configuration

### "Variable d'environnement PENNYLANE_API_KEY requise"

**Cause:** Fichier `.env` absent ou mal configuré

**Solution:**

```bash
# 1. Vérifier que .env existe
ls -la .env  # Linux/Mac
dir .env     # Windows

# 2. Si absent, créer depuis template
cp .env.example .env

# 3. Éditer et configurer
nano .env
```

### "Clé API Pennylane invalide"

**Cause:** API key incorrecte ou contenant des espaces

**Solution:**

```bash
# Vérifier format dans .env (pas d'espaces)
PENNYLANE_API_KEY=pl_live_abc123...
```

!!! tip "Obtenir nouvelle clé"
    [app.pennylane.com](https://app.pennylane.com) → Paramètres → API

## Erreurs PostgreSQL

### "Erreur connexion PostgreSQL"

**Cause:** Docker pas démarré ou conteneur arrêté

**Solution:**

```bash
# 1. Vérifier Docker Desktop
docker --version

# 2. Vérifier conteneurs
docker ps

# 3. Redémarrer si nécessaire
docker-compose restart postgres

# 4. Logs PostgreSQL
docker logs pennylane_postgres
```

### "Mot de passe PostgreSQL invalide"

**Cause:** Password dans `.env` différent de celui configuré

**Solution:**

```bash
# 1. Arrêter et supprimer volumes
docker-compose down -v

# 2. Configurer nouveau password dans .env
nano .env

# 3. Redémarrer
docker-compose up -d
```

### "Table introuvable"

**Cause:** Base non initialisée ou extraction pas lancée

**Solution:**

```bash
# Lancer première extraction
cd src
python main.py full
```

## Erreurs API Pennylane

### "Rate limit dépassé (429)"

**Cause:** Trop de requêtes en peu de temps

**Solution:** Le script gère automatiquement, mais si persistant :

```env
# Réduire dans .env
PENNYLANE_RATE_LIMIT=3.0
```

### "Endpoint non trouvé (404)"

**Cause:** Endpoint incorrect dans `config.json`

**Solution:**

Vérifier dans [documentation API Pennylane](https://pennylane.readme.io/)

### "Timeout API"

**Cause:** Connexion lente ou API indisponible

**Solution:**

```bash
# Vérifier connexion internet
ping app.pennylane.com

# Vérifier status API
curl https://status.pennylane.com
```

## Erreurs d'extraction

### "Aucune donnée extraite"

**Cause:** Filtre incrémentiel trop restrictif ou pas de nouvelles données

**Solution:**

```bash
# Forcer extraction complète
python main.py full
```

### "Extraction très lente"

**Cause:** Gros volume ou rate limiting

**Solution:**

- Patience (normal pour première extraction)
- Vérifier logs : `tail -f logs/pennylane_etl.log`
- Limiter endpoints dans `config.json`

## Erreurs Python

### "ModuleNotFoundError"

**Cause:** Dépendances non installées

**Solution:**

```bash
pip install -r requirements.txt --upgrade
```

### "ImportError: config_loader"

**Cause:** Pas dans bon répertoire

**Solution:**

```bash
# Toujours lancer depuis src/
cd src
python main.py full
```

## Problèmes Docker

### "Cannot connect to Docker daemon"

**Cause:** Docker Desktop pas démarré

**Solution:**

1. Démarrer Docker Desktop
2. Attendre initialisation complète
3. Relancer `docker-compose up -d`

### "Port 5432 déjà utilisé"

**Cause:** Autre PostgreSQL actif

**Solution:**

```bash
# Option 1: Arrêter autre PostgreSQL
# Option 2: Changer port dans .env
POSTGRES_PORT=5433
```

### "Port 5050 déjà utilisé"

**Solution:**

```env
# Changer port pgAdmin
PGADMIN_PORT=5051
```

## Logs et diagnostics

### Consulter tous les logs

```bash
# Logs application
cat logs/pennylane_etl.log

# Logs PostgreSQL
docker logs pennylane_postgres

# Logs pgAdmin
docker logs pennylane_pgadmin
```

### Niveau DEBUG

Pour diagnostics détaillés :

```env
# Dans .env
LOG_LEVEL=DEBUG
```

### Vérifier tables créées

```sql
SELECT table_name,
       (SELECT COUNT(*) FROM pennylane.table_name) as row_count
FROM information_schema.tables
WHERE table_schema = 'pennylane';
```

### Vérifier logs ETL

```sql
SELECT *
FROM pennylane.etl_logs
WHERE status = 'failed'
ORDER BY execution_date DESC
LIMIT 10;
```

## Réinitialisation complète

Si rien ne fonctionne, réinitialisation totale :

```bash
# 1. Arrêter tout
docker-compose down -v

# 2. Supprimer logs
rm -rf logs/*

# 3. Vérifier .env
cat .env

# 4. Réinstaller dépendances
pip install -r requirements.txt --force-reinstall

# 5. Redémarrer
docker-compose up -d
sleep 10
cd src && python main.py full
```

## Support

Si problème persiste :

1. **Vérifier issues GitHub** : [github.com/yves34690/Penny/issues](https://github.com/yves34690/Penny/issues)
2. **Créer nouvelle issue** avec :
   - Message d'erreur complet
   - Logs pertinents
   - Étapes pour reproduire
3. **Documentation Pennylane** : [pennylane.readme.io](https://pennylane.readme.io/)
