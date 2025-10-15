# Guide d'automatisation Penny

## 🎯 Pour qui est ce guide ?

Ce guide s'adresse à **tous les utilisateurs**, même sans connaissance technique. Nous expliquons **chaque étape** en détail, y compris comment ouvrir un terminal Windows.

## Vue d'ensemble

Le projet Penny inclut maintenant un système d'**actualisation automatique** via Docker qui synchronise vos données Pennylane → PostgreSQL **toutes les 2 heures** sans intervention manuelle.

**En d'autres termes** : Une fois configuré, vous n'avez plus rien à faire ! Les données se mettent à jour automatiquement en arrière-plan.

## Architecture

```
Docker Compose
├── PostgreSQL (port 5433)     → Base de données
├── pgAdmin (port 5050)        → Interface graphique
└── Scheduler (automatique)    → Synchronisation toutes les 2h
```

## 🚀 Installation et démarrage

### Préambule : Comment ouvrir un terminal Windows ?

**Pour exécuter les commandes de ce guide, vous devez ouvrir un terminal Windows. Voici comment :**

#### Méthode 1 : PowerShell (Recommandé)
1. Appuyez sur la touche **Windows** de votre clavier
2. Tapez `PowerShell`
3. Cliquez sur **Windows PowerShell** dans les résultats
4. Une fenêtre bleue s'ouvre → c'est votre terminal !

#### Méthode 2 : Invite de commandes
1. Appuyez sur **Windows + R**
2. Tapez `cmd`
3. Appuyez sur **Entrée**
4. Une fenêtre noire s'ouvre → c'est votre terminal !

#### Méthode 3 : Depuis l'explorateur de fichiers
1. Ouvrez l'explorateur de fichiers
2. Naviguez jusqu'au dossier `C:\Penny`
3. Dans la barre d'adresse en haut, tapez `cmd` puis **Entrée**
4. Le terminal s'ouvre directement dans le bon dossier !

**📝 Note importante** :
- Toutes les commandes de ce guide doivent être exécutées **dans le terminal**
- Quand on écrit `docker-compose up -d`, vous devez **taper cette commande dans le terminal** puis appuyer sur **Entrée**

---

### 1. Configuration initiale

Assurez-vous que votre fichier `.env` contient tous les credentials nécessaires :

```env
# PostgreSQL local
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=pennylane_db
POSTGRES_USER=pennylane_user
POSTGRES_PASSWORD=votre_mot_de_passe

# Pennylane Data Sharing (Redshift)
PENNYLANE_DATA_SHARING_KEY=votre_token_data_sharing
REDSHIFT_HOST=pennylane-external.csqwamh5pldr.eu-west-1.redshift.amazonaws.com
REDSHIFT_PORT=5439
REDSHIFT_DATABASE=prod
REDSHIFT_USER=votre_user_redshift

# Pennylane API REST
PENNYLANE_API_TOKEN=votre_token_api_rest

# pgAdmin
PGADMIN_EMAIL=admin@penny.com
PGADMIN_PASSWORD=votre_password_pgadmin
PGADMIN_PORT=5050
```

### 2. Démarrer le système complet

**Ouvrez un terminal** (voir instructions ci-dessus), naviguez vers le dossier du projet, puis tapez cette commande :

```bash
cd C:\Penny
docker-compose up -d
```

**Explication** :
- `cd C:\Penny` → Se déplace dans le dossier du projet
- `docker-compose up -d` → Démarre tous les services en arrière-plan (le `-d` signifie "détaché", c'est-à-dire que ça tourne en arrière-plan)

**C'est tout !** Le système est maintenant automatique :
- ✅ PostgreSQL démarre sur le port 5433
- ✅ pgAdmin démarre sur [http://localhost:5050](http://localhost:5050)
- ✅ Le scheduler démarre automatiquement et exécute immédiatement une première synchronisation
- ✅ Ensuite, le scheduler se déclenche automatiquement **toutes les 2 heures**

### 🔄 En cas de redémarrage du PC

Si vous redémarrez votre ordinateur, Docker s'arrête. Pour **relancer le système**, il suffit de :

**Étape 1 : Ouvrir un terminal**
- Appuyez sur la touche **Windows**
- Tapez `PowerShell`
- Cliquez sur **Windows PowerShell**

**Étape 2 : Lancer cette commande unique**
```bash
cd C:\Penny && docker-compose up -d
```

**C'est tout !** Le système redémarre automatiquement et reprend la synchronisation.

**💡 Astuce pour les experts** : Pour que Docker démarre automatiquement au démarrage de Windows, voir la section [Démarrage automatique au boot](#démarrage-automatique-au-boot-windows) plus bas dans ce guide.

### 3. Vérifier que tout fonctionne

#### Vérifier l'état des conteneurs

**Dans votre terminal**, tapez :

```bash
docker-compose ps
```

Vous devriez voir 3 conteneurs en cours d'exécution :
```
NAME                  STATUS
pennylane_postgres    Up (healthy)
pennylane_pgadmin     Up
pennylane_scheduler   Up (healthy)
```

#### Suivre les logs du scheduler en temps réel

**Dans votre terminal**, tapez :

```bash
docker-compose logs scheduler -f
```

**Note** : Pour arrêter l'affichage des logs, appuyez sur **Ctrl + C**

Vous verrez :
```
[DEMARRAGE] Notebook Scheduler Pennylane
[DEMARRAGE] Actualisation toutes les 2 heures
[SYNC] DEBUT synchronisation - 2025-10-15 14:21:06
[EXECUTE] Clients (API REST)
[OK] Table 'customers' exportee : 7 lignes
[EXECUTE] Factures clients (API REST)
...
[SYNC] Succes: 12/12 | Erreurs: 0
[CRON] Prochaine execution dans 2h
```

## Fonctionnement automatique

### Que se passe-t-il ?

1. **Au démarrage** : Le scheduler exécute immédiatement les 12 notebooks pour synchroniser toutes les données
2. **Toutes les 2 heures** : Le scheduler se réveille automatiquement et re-synchronise les données
3. **En cas d'erreur** : Le scheduler continue de fonctionner et réessaiera à la prochaine exécution
4. **Au redémarrage** : Si vous redémarrez votre PC, relancer `docker-compose up -d` et tout reprend automatiquement

### Redémarrage automatique

Le scheduler est configuré avec `restart: always`, ce qui signifie :
- ✅ Il redémarre automatiquement en cas de crash
- ✅ Il redémarre automatiquement après un reboot du PC (si Docker Desktop est configuré pour démarrer au boot)

## Gestion du système

**Important** : Toutes les commandes ci-dessous doivent être exécutées **dans un terminal** (PowerShell ou invite de commandes), dans le dossier `C:\Penny`.

### Arrêter le système

**Ouvrez un terminal** puis tapez :

```bash
cd C:\Penny
docker-compose down
```

**Résultat** : Cela arrête tous les conteneurs (PostgreSQL, pgAdmin, Scheduler).

### Redémarrer le système

**Dans votre terminal**, tapez :

```bash
docker-compose restart
```

**Résultat** : Tous les services redémarrent sans perdre les données.

### Forcer une synchronisation immédiate

Si vous voulez forcer une synchronisation sans attendre les 2 heures :

**Option 1 : Redémarrer uniquement le scheduler** (recommandé)
```bash
docker-compose restart scheduler
```

**Option 2 : Exécuter manuellement avec Python**
```bash
python src/notebook_scheduler.py
```
**Note** : Cette commande bloque le terminal. Appuyez sur **Ctrl + C** pour arrêter.

### Vérifier les logs complets

**Dans votre terminal**, tapez une de ces commandes :

```bash
# Logs du scheduler uniquement
docker-compose logs scheduler

# Logs de PostgreSQL uniquement
docker-compose logs postgres

# Logs de tous les services
docker-compose logs

# Logs en temps réel (appuyez sur Ctrl+C pour arrêter)
docker-compose logs -f
```

## Connexion Power BI

Avec le système automatique, vous pouvez configurer Power BI en **mode DirectQuery** pour avoir des données toujours à jour :

### Paramètres de connexion

| Paramètre | Valeur |
|-----------|--------|
| Serveur | `localhost:5433` |
| Base de données | `pennylane_db` |
| Utilisateur | `pennylane_user` |
| Mot de passe | (celui configuré dans `.env`) |
| Schema | `pennylane` |

### Mode de connexion recommandé

- **DirectQuery** : Les données sont toujours synchronisées avec PostgreSQL (rafraîchissement automatique toutes les 2h)
- **Import** : Vous devez rafraîchir manuellement dans Power BI (mais plus rapide pour les visualisations)

## Maintenance

### Sauvegarder les données PostgreSQL

```bash
# Exporter la base de données
docker exec pennylane_postgres pg_dump -U pennylane_user pennylane_db > backup.sql

# Restaurer la base de données
cat backup.sql | docker exec -i pennylane_postgres psql -U pennylane_user pennylane_db
```

### Nettoyer les logs anciens

Les outputs des notebooks sont sauvegardés dans `data/outputs/`. Pour nettoyer les anciens :

```bash
# Windows
del /Q "data\outputs\*.ipynb"

# Linux/Mac
rm -f data/outputs/*.ipynb
```

### Mettre à jour le système

```bash
# 1. Arrêter le système
docker-compose down

# 2. Tirer les dernières modifications (si projet Git)
git pull

# 3. Reconstruire les images Docker
docker-compose build --no-cache

# 4. Redémarrer
docker-compose up -d
```

## Démarrage automatique au boot (Windows)

Pour que Docker Compose démarre automatiquement au démarrage de Windows :

### Option 1 : Docker Desktop Auto-start

1. Ouvrir **Docker Desktop**
2. Aller dans **Settings** → **General**
3. Cocher **"Start Docker Desktop when you log in"**
4. Ajouter un script de démarrage :

Créer un fichier `start_penny.bat` :
```bat
@echo off
cd C:\Penny
docker-compose up -d
```

5. Ajouter `start_penny.bat` aux programmes de démarrage Windows :
   - Appuyer sur `Win + R`
   - Taper `shell:startup`
   - Copier le fichier `.bat` dans ce dossier

### Option 2 : Windows Task Scheduler

1. Ouvrir **Planificateur de tâches**
2. Créer une nouvelle tâche
3. **Déclencheur** : "Au démarrage"
4. **Action** : `C:\Penny\start_penny.bat`
5. **Paramètres** : Cocher "Exécuter même si l'utilisateur n'est pas connecté"

## Troubleshooting

### Le scheduler ne démarre pas

```bash
# Vérifier les logs d'erreur
docker-compose logs scheduler --tail 50

# Vérifier que PostgreSQL est accessible
docker-compose exec scheduler ping postgres -c 3
```

### Les notebooks échouent

```bash
# Vérifier les credentials dans .env
cat .env

# Tester la connexion Redshift manuellement
python tests/test_redshift.py

# Vérifier les outputs des notebooks pour voir les erreurs détaillées
ls -lh data/outputs/
```

### PostgreSQL est inaccessible

```bash
# Vérifier que le port 5433 n'est pas utilisé
netstat -an | findstr 5433

# Redémarrer PostgreSQL
docker-compose restart postgres
```

### Port 5433 déjà utilisé

Si le port 5433 est déjà utilisé sur votre machine, modifiez `.env` :

```env
POSTGRES_PORT=5434  # ou un autre port libre
```

Puis recréez les conteneurs :
```bash
docker-compose down
docker-compose up -d
```

## Monitoring avancé

### Vérifier la santé des services

```bash
# Commande Docker native
docker-compose ps

# Détails du scheduler
docker inspect pennylane_scheduler
```

### Statistiques d'utilisation des ressources

```bash
# CPU, RAM, Network de tous les conteneurs
docker stats
```

### Logs structurés

Le scheduler écrit également des logs dans `logs/scheduler.log` à l'intérieur du conteneur :

```bash
docker-compose exec scheduler tail -f logs/scheduler.log
```

## FAQ

### Puis-je changer la fréquence d'actualisation ?

Oui, éditez `src/notebook_scheduler.py` ligne 273 :

```python
# Actuellement : toutes les 2 heures
schedule.every(2).hours.do(self.run_sync)

# Exemples d'alternatives :
schedule.every(10).minutes.do(self.run_sync)  # Toutes les 10 minutes
schedule.every().hour.do(self.run_sync)       # Toutes les heures
schedule.every().day.at("09:00").do(self.run_sync)  # Tous les jours à 9h
```

Puis reconstruisez le scheduler :
```bash
docker-compose up -d --build scheduler
```

### Puis-je désactiver certains notebooks ?

Oui, éditez `src/notebook_scheduler.py` et commentez les notebooks que vous ne voulez pas synchroniser dans la liste `self.notebooks` (lignes 21-141).

### Les données sont-elles sauvegardées si je stoppe Docker ?

**Oui** : PostgreSQL utilise un volume Docker (`postgres_data`) qui persiste même après `docker-compose down`. Pour effacer complètement les données :

```bash
docker-compose down -v  # Supprime aussi les volumes
```

### Puis-je utiliser le système sans Docker ?

Oui, vous pouvez exécuter manuellement le scheduler :

```bash
python src/notebook_scheduler.py
```

Mais Docker offre l'avantage de l'automatisation complète et du redémarrage automatique.

---

**Date de création** : 2025-10-15
**Dernière mise à jour** : 2025-10-15
**Version** : 1.0.0
