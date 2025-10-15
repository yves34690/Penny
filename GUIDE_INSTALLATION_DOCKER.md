# 🐳 Guide d'Installation Docker Desktop & PostgreSQL

**Objectif** : Installer Docker Desktop et démarrer PostgreSQL en 15 minutes.

**Public** : Débutants complets, aucune connaissance Docker requise.

---

## 📋 Table des matières

1. [Qu'est-ce que Docker ?](#1-quest-ce-que-docker-)
2. [Prérequis système](#2-prérequis-système)
3. [Installation Windows](#3-installation-windows)
4. [Installation Mac](#4-installation-mac)
5. [Installation Linux](#5-installation-linux)
6. [Démarrer PostgreSQL](#6-démarrer-postgresql)
7. [Vérifier l'installation](#7-vérifier-linstallation)
8. [Accès pgAdmin](#8-accès-pgadmin)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Qu'est-ce que Docker ? 🤔

### En une phrase
**Docker est comme une "machine à café capsules" pour logiciels** : il permet d'installer PostgreSQL en une commande, sans configuration manuelle compliquée.

### Pourquoi utiliser Docker ?

| Sans Docker | Avec Docker |
|-------------|-------------|
| ❌ Installer PostgreSQL manuellement | ✅ 1 commande : `docker-compose up` |
| ❌ Configurer utilisateur, ports, permissions | ✅ Tout pré-configuré dans `docker-compose.yml` |
| ❌ Risque conflits avec autres installations | ✅ Isolé dans un conteneur |
| ❌ Difficile à désinstaller proprement | ✅ `docker-compose down` → tout supprimé |
| ❌ Nécessite expertise admin système | ✅ Accessible aux débutants |

**Analogie** : Docker = Lego pour logiciels. Assemblez des "briques" (conteneurs) sans construire chaque pièce à la main.

---

## 2. Prérequis système

### Windows

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| **OS** | Windows 10 64-bit (version 1903+) | Windows 11 |
| **RAM** | 4 GB | 8 GB+ |
| **Processeur** | Compatible virtualisation (VT-x/AMD-V) | Intel Core i5+ |
| **Espace disque** | 10 GB libres | 20 GB+ |
| **WSL 2** | Requis | Installé automatiquement |

### Mac

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| **OS** | macOS 11 Big Sur | macOS 13+ |
| **RAM** | 4 GB | 8 GB+ |
| **Processeur** | Intel ou Apple Silicon (M1/M2/M3) | Apple Silicon |
| **Espace disque** | 10 GB libres | 20 GB+ |

### Linux

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| **Distribution** | Ubuntu 20.04+, Debian 10+ | Ubuntu 22.04+ |
| **RAM** | 4 GB | 8 GB+ |
| **Kernel** | Linux 4.0+ | Linux 5.0+ |
| **Espace disque** | 10 GB libres | 20 GB+ |

---

## 3. Installation Windows 🪟

### Étape 1 : Vérifier la virtualisation

1. **Ouvrir le Gestionnaire des tâches** (`Ctrl + Shift + Esc`)
2. Onglet **Performance** → **CPU**
3. Vérifier **"Virtualisation: Activée"**

**Si désactivée** :
- Redémarrer le PC
- Entrer dans le BIOS (touche `F2`, `Del` ou `F10` au démarrage)
- Chercher **Intel VT-x** ou **AMD-V**
- **Activer** → Sauvegarder et redémarrer

### Étape 2 : Télécharger Docker Desktop

1. **Visiter** : [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. **Cliquer** sur **"Download for Windows"**
3. **Attendre** le téléchargement (`Docker Desktop Installer.exe`, ~500 MB)

### Étape 3 : Installer Docker Desktop

1. **Double-cliquer** sur `Docker Desktop Installer.exe`
2. **Cocher** : ✅ "Use WSL 2 instead of Hyper-V" (recommandé)
3. **Cliquer** : "Ok" → Installation commence
4. **Attendre** 5-10 minutes (télécharge WSL 2 si nécessaire)
5. **Redémarrer l'ordinateur** quand demandé

### Étape 4 : Première configuration

1. **Lancer Docker Desktop** depuis le Menu Démarrer
2. **Accepter** les conditions d'utilisation
3. **Choisir** : "Use recommended settings" (paramètres par défaut)
4. **Patienter** : Docker démarre (icône Docker apparaît dans la barre des tâches)

### Étape 5 : Vérifier l'installation

**Ouvrir PowerShell ou Invite de commandes** :

```powershell
docker --version
```

**Résultat attendu** :
```
Docker version 24.0.7, build afdd53b
```

✅ **Si vous voyez une version**, Docker est installé !

---

## 4. Installation Mac 🍎

### Étape 1 : Choisir la bonne version

**Vérifier votre processeur** :
1. **Menu Pomme**  → **À propos de ce Mac**
2. Regarder **"Processeur"** ou **"Puce"**

| Processeur | Version Docker |
|------------|----------------|
| **Intel** (Core i5, i7, i9) | Docker Desktop for Mac (Intel chip) |
| **Apple Silicon** (M1, M2, M3) | Docker Desktop for Mac (Apple Silicon) |

### Étape 2 : Télécharger Docker Desktop

1. **Visiter** : [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. **Cliquer** sur la version correspondant à votre processeur
3. **Télécharger** le fichier `.dmg` (~600 MB)

### Étape 3 : Installer

1. **Double-cliquer** sur `Docker.dmg`
2. **Glisser** l'icône Docker vers le dossier **Applications**
3. **Ouvrir** Docker depuis **Applications**
4. **Autoriser** l'accès (entrer mot de passe admin si demandé)
5. **Accepter** les conditions d'utilisation

### Étape 4 : Vérifier l'installation

**Ouvrir Terminal** (`Cmd + Espace` → "Terminal") :

```bash
docker --version
```

**Résultat attendu** :
```
Docker version 24.0.7, build afdd53b
```

---

## 5. Installation Linux 🐧

### Ubuntu / Debian

```bash
# 1. Mettre à jour les packages
sudo apt-get update

# 2. Installer dépendances
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Ajouter clé GPG Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. Ajouter repository Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Installer Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 6. Ajouter votre utilisateur au groupe docker (évite sudo)
sudo usermod -aG docker $USER

# 7. Redémarrer session (ou reboot)
newgrp docker

# 8. Vérifier installation
docker --version
```

### Fedora / RHEL / CentOS

```bash
# 1. Installer dnf-plugins
sudo dnf -y install dnf-plugins-core

# 2. Ajouter repository
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# 3. Installer Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 4. Démarrer Docker
sudo systemctl start docker
sudo systemctl enable docker

# 5. Ajouter utilisateur au groupe
sudo usermod -aG docker $USER
newgrp docker

# 6. Vérifier
docker --version
```

---

## 6. Démarrer PostgreSQL 🚀

### Méthode 1 : Avec docker-compose (Recommandé ⭐)

**Ce projet inclut déjà un fichier `docker-compose.yml` pré-configuré.**

1. **Ouvrir un terminal** dans le dossier `Penny` :

```bash
# Windows (PowerShell)
cd C:\Penny

# Mac/Linux
cd ~/Penny
```

2. **Lancer PostgreSQL** :

```bash
docker-compose up -d
```

**Résultat attendu** :
```
[+] Running 2/2
 ✔ Container postgres  Started
 ✔ Container pgadmin   Started
```

3. **Vérifier que ça tourne** :

```bash
docker ps
```

**Résultat attendu** :
```
CONTAINER ID   IMAGE           PORTS                    STATUS
abc123...      postgres:15     0.0.0.0:5433->5432/tcp   Up
def456...      dpage/pgadmin4  0.0.0.0:5050->80/tcp     Up
```

✅ **Si vous voyez 2 conteneurs "Up"**, PostgreSQL fonctionne !

### Méthode 2 : Commande Docker manuelle (Alternative)

Si vous n'avez pas de `docker-compose.yml` :

```bash
# Lancer PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_USER=pennylane_user \
  -e POSTGRES_PASSWORD=votre_mot_de_passe \
  -e POSTGRES_DB=pennylane_db \
  -p 5433:5432 \
  postgres:15

# Lancer pgAdmin
docker run -d \
  --name pgadmin \
  -e PGADMIN_DEFAULT_EMAIL=admin@admin.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  -p 5050:80 \
  dpage/pgadmin4
```

---

## 7. Vérifier l'installation ✅

### Test 1 : Connexion PostgreSQL

```bash
# Depuis votre machine hôte
psql -h localhost -p 5433 -U pennylane_user -d pennylane_db
```

**Si psql n'est pas installé**, utilisez Docker :

```bash
docker exec -it postgres psql -U pennylane_user -d pennylane_db
```

**Résultat attendu** :
```
pennylane_db=#
```

**Commande test** :
```sql
SELECT version();
```

Vous devriez voir la version de PostgreSQL.

**Quitter** : `\q`

### Test 2 : Connexion Python

Créer un fichier test `test_postgres.py` :

```python
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="pennylane_db",
        user="pennylane_user",
        password="votre_mot_de_passe"  # Celui de votre .env
    )
    print("✅ Connexion PostgreSQL réussie !")
    conn.close()
except Exception as e:
    print(f"❌ Erreur : {e}")
```

**Exécuter** :
```bash
python test_postgres.py
```

---

## 8. Accès pgAdmin 🖥️

**pgAdmin** = Interface web pour gérer PostgreSQL (comme Excel pour bases de données).

### Étape 1 : Ouvrir pgAdmin

1. **Navigateur web** → [http://localhost:5050](http://localhost:5050)
2. **Connexion** :
   - Email : `admin@admin.com`
   - Password : `admin`

### Étape 2 : Ajouter serveur PostgreSQL

1. **Clic droit** sur "Servers" (barre latérale gauche)
2. **Create** → **Server**
3. **Onglet "General"** :
   - Name : `Pennylane Local`
4. **Onglet "Connection"** :
   - Host : `host.docker.internal` (Windows/Mac) ou `172.17.0.1` (Linux)
   - Port : `5432` (port interne Docker, pas 5433 !)
   - Database : `pennylane_db`
   - Username : `pennylane_user`
   - Password : (votre mot de passe .env)
   - ✅ Cocher "Save password"
5. **Save**

### Étape 3 : Explorer les données

1. **Développer** : Servers → Pennylane Local → Databases → pennylane_db → Schemas → pennylane → Tables
2. **Clic droit** sur une table → **View/Edit Data** → **All Rows**

---

## 9. Troubleshooting 🔧

### ❌ Problème : "Docker daemon not running"

**Cause** : Docker Desktop n'est pas démarré.

**Solution** :
- Windows/Mac : Lancer Docker Desktop depuis le menu Démarrer/Applications
- Linux : `sudo systemctl start docker`

---

### ❌ Problème : "Port 5433 already in use"

**Cause** : Un autre service utilise le port 5433.

**Solution 1** : Changer le port dans `docker-compose.yml`

```yaml
ports:
  - "5434:5432"  # Au lieu de 5433
```

**Solution 2** : Trouver et arrêter le service qui utilise 5433

```bash
# Windows
netstat -ano | findstr :5433

# Mac/Linux
lsof -i :5433
```

---

### ❌ Problème : "Cannot connect to PostgreSQL from Python"

**Diagnostic** :

```bash
# Vérifier que PostgreSQL écoute
docker exec postgres pg_isready

# Vérifier les logs
docker logs postgres
```

**Causes fréquentes** :
1. **Mauvais port** : Utilisez `5433` (externe), pas `5432`
2. **Mauvais credentials** : Vérifier `.env`
3. **Firewall** : Autoriser port 5433
4. **PostgreSQL n'a pas démarré** : `docker-compose restart`

---

### ❌ Problème : "WSL 2 installation incomplete" (Windows)

**Solution** :

1. **Ouvrir PowerShell en admin**
2. **Installer WSL 2** :

```powershell
wsl --install
wsl --set-default-version 2
```

3. **Redémarrer** l'ordinateur
4. **Relancer Docker Desktop**

---

### ❌ Problème : pgAdmin "host.docker.internal" ne fonctionne pas

**Solution Linux** :

Remplacer `host.docker.internal` par l'IP de votre conteneur PostgreSQL :

```bash
# Obtenir l'IP
docker inspect postgres | grep IPAddress
```

Utiliser cette IP dans pgAdmin (ex: `172.17.0.2`).

---

### ❌ Problème : "Permission denied" (Linux)

**Cause** : Utilisateur pas dans groupe `docker`.

**Solution** :

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Ou préfixer avec `sudo` :
```bash
sudo docker-compose up -d
```

---

## 🎓 Commandes utiles

### Gestion conteneurs

```bash
# Démarrer PostgreSQL
docker-compose up -d

# Arrêter PostgreSQL
docker-compose down

# Arrêter ET supprimer données
docker-compose down -v

# Redémarrer
docker-compose restart

# Voir les logs
docker-compose logs -f postgres

# Voir les conteneurs actifs
docker ps

# Voir TOUS les conteneurs
docker ps -a
```

### Accès direct PostgreSQL

```bash
# Entrer dans le conteneur
docker exec -it postgres bash

# Accès psql
docker exec -it postgres psql -U pennylane_user -d pennylane_db

# Sauvegarder base de données
docker exec postgres pg_dump -U pennylane_user pennylane_db > backup.sql

# Restaurer base de données
docker exec -i postgres psql -U pennylane_user -d pennylane_db < backup.sql
```

### Nettoyage Docker

```bash
# Supprimer conteneurs arrêtés
docker container prune

# Supprimer images inutilisées
docker image prune

# Nettoyage complet (ATTENTION : supprime TOUT)
docker system prune -a
```

---

## 📊 Récapitulatif visuel

```
┌─────────────────────────────────────────────────────┐
│  1. INSTALLER Docker Desktop                        │
│     Windows/Mac : Installateur graphique           │
│     Linux : apt-get install docker                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  2. VÉRIFIER installation                           │
│     $ docker --version                              │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  3. LANCER PostgreSQL                               │
│     $ docker-compose up -d                          │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  4. VÉRIFIER fonctionnement                         │
│     $ docker ps                                     │
│     → 2 conteneurs "Up"                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  5. ACCÉDER pgAdmin                                 │
│     http://localhost:5050                           │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Checklist finale

Avant de passer à la suite, vérifiez :

- [ ] Docker installé (`docker --version` fonctionne)
- [ ] Docker Desktop lancé (icône dans barre des tâches)
- [ ] PostgreSQL démarré (`docker ps` montre 2 conteneurs)
- [ ] Connexion PostgreSQL testée (Python ou psql)
- [ ] pgAdmin accessible (http://localhost:5050)
- [ ] Serveur PostgreSQL ajouté dans pgAdmin

**Si tout est coché, passez à l'étape suivante** : [GUIDE_DEBUTANT.md](GUIDE_DEBUTANT.md) 🎉

---

## 📚 Ressources complémentaires

- **Documentation Docker officielle** : [docs.docker.com](https://docs.docker.com/)
- **PostgreSQL avec Docker** : [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- **Tutoriel DataCamp** : [PostgreSQL in Docker](https://www.datacamp.com/tutorial/postgresql-docker)
- **Troubleshooting Docker** : [Docker Desktop Troubleshooting](https://docs.docker.com/desktop/troubleshoot/overview/)

---

**Besoin d'aide ?** Ouvrez une issue sur [GitHub Issues](https://github.com/votre-username/Penny/issues) !

*Guide créé avec ❤️ pour la communauté Pennylane*
