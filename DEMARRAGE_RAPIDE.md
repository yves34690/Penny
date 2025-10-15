# 🚀 Démarrage rapide Penny - Pour débutants

## 🎯 Vous êtes ici parce que...

Vous voulez **synchroniser vos données Pennylane** vers votre ordinateur pour les analyser avec **Power BI**.

**Bonne nouvelle** : C'est très simple ! Suivez ce guide pas à pas.

---

## 📋 De quoi avez-vous besoin ?

- ✅ Un **ordinateur Windows** (Mac et Linux fonctionnent aussi)
- ✅ Une **connexion Internet**
- ✅ **10 minutes** de votre temps
- ✅ Vos **clés Pennylane** (on vous explique comment les obtenir)

**Aucune connaissance en programmation n'est requise !**

---

## 🔧 Étape 1 : Installer les outils nécessaires (5 min)

### 1.1 Installer Python

**C'est quoi Python ?** Un logiciel qui permet d'exécuter le système Penny.

**Comment l'installer ?**
1. Allez sur [python.org/downloads](https://www.python.org/downloads/)
2. Cliquez sur le gros bouton **"Download Python 3.12"**
3. Ouvrez le fichier téléchargé
4. **IMPORTANT** : Cochez la case **"Add Python to PATH"** en bas de la fenêtre
5. Cliquez sur **"Install Now"**
6. Attendez la fin de l'installation
7. Cliquez sur **"Close"**

**Comment vérifier que c'est installé ?**
1. Appuyez sur la touche **Windows** de votre clavier
2. Tapez `cmd`
3. Appuyez sur **Entrée** (une fenêtre noire s'ouvre)
4. Tapez `python --version` puis **Entrée**
5. Vous devez voir quelque chose comme `Python 3.12.0`

✅ **Si vous voyez un numéro de version** : C'est bon !
❌ **Si vous voyez une erreur** : Recommencez l'installation en cochant bien "Add Python to PATH"

---

### 1.2 Installer Docker Desktop

**C'est quoi Docker ?** Un logiciel qui permet de faire tourner la base de données PostgreSQL facilement.

**Comment l'installer ?**
1. Allez sur [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Cliquez sur **"Download for Windows"**
3. Ouvrez le fichier téléchargé
4. Suivez les instructions d'installation (cliquez sur "Suivant" à chaque fois)
5. **Redémarrez votre ordinateur** si demandé
6. Lancez **Docker Desktop** depuis le menu Démarrer
7. Attendez que Docker démarre (icône en bas à droite qui devient verte)

**Comment vérifier que c'est installé ?**
1. Regardez en bas à droite de votre écran (barre des tâches)
2. Vous devez voir une petite icône de **baleine** (logo Docker)
3. Si elle est **verte** : C'est bon !
4. Si elle est **rouge ou orange** : Attendez quelques secondes

---

### 1.3 Installer Git

**C'est quoi Git ?** Un logiciel pour télécharger le projet Penny depuis Internet.

**Comment l'installer ?**
1. Allez sur [git-scm.com/downloads](https://git-scm.com/downloads)
2. Cliquez sur **"Download for Windows"**
3. Ouvrez le fichier téléchargé
4. Cliquez sur **"Next"** à chaque étape (les options par défaut sont bien)
5. Cliquez sur **"Install"**
6. Cliquez sur **"Finish"**

---

## 📥 Étape 2 : Télécharger le projet Penny (1 min)

**Maintenant, on va télécharger le projet Penny sur votre ordinateur.**

### 2.1 Ouvrir un terminal

1. Appuyez sur la touche **Windows** de votre clavier
2. Tapez `PowerShell`
3. Cliquez sur **Windows PowerShell** dans les résultats
4. Une **fenêtre bleue** s'ouvre → c'est votre **terminal** !

**Note** : Le terminal, c'est une fenêtre où on tape des commandes au lieu de cliquer avec la souris.

---

### 2.2 Télécharger Penny

**Dans votre terminal**, tapez cette commande **exactement comme elle est écrite** :

```bash
git clone https://github.com/yves34690/Penny.git
```

**Puis appuyez sur Entrée**.

**Vous devez voir** :
```
Cloning into 'Penny'...
remote: Counting objects...
...
```

Attendez quelques secondes. Le projet se télécharge.

**Ensuite, tapez cette commande** :

```bash
cd Penny
```

**Puis appuyez sur Entrée**.

**Explication** : Cette commande "entre" dans le dossier Penny que vous venez de télécharger.

---

## 🔑 Étape 3 : Configurer vos clés Pennylane (2 min)

### 3.1 Où trouver vos clés Pennylane ?

**Vous avez besoin de 2 clés** :

#### Clé 1 : Token API REST
1. Connectez-vous à votre compte Pennylane
2. Allez dans **Paramètres** → **Développeurs** → **API**
3. Cliquez sur **"Créer un token"**
4. Copiez le token (une longue suite de lettres et chiffres)

#### Clé 2 : Token Data Sharing (Redshift)
1. Toujours dans **Paramètres** → **Développeurs**
2. Allez dans l'onglet **Data Sharing**
3. Copiez le **"Data Sharing Key"**

**Gardez ces 2 clés quelque part**, vous allez en avoir besoin dans 2 minutes.

---

### 3.2 Créer le fichier de configuration

**Dans votre terminal**, tapez cette commande :

```bash
cp .env.example .env
```

**Puis appuyez sur Entrée**.

**Explication** : Cette commande crée un fichier `.env` qui va contenir vos clés.

---

### 3.3 Remplir vos clés

**Maintenant, on va ouvrir le fichier `.env` pour y mettre vos clés.**

**Option 1 : Avec le Bloc-notes** (le plus simple)
1. Ouvrez l'**Explorateur de fichiers**
2. Allez dans `C:\Users\VOTRE_NOM\Penny` (ou là où vous avez téléchargé le projet)
3. Vous voyez un fichier qui s'appelle `.env` (il peut s'appeler juste `env`)
4. **Clic droit** sur ce fichier → **Ouvrir avec** → **Bloc-notes**
5. Vous voyez plein de lignes de texte

**Option 2 : Avec la commande** (plus rapide)

Dans votre terminal, tapez :
```bash
notepad .env
```

**Puis appuyez sur Entrée**. Le fichier s'ouvre dans le Bloc-notes.

---

### 3.4 Remplir les valeurs

**Dans le fichier `.env` ouvert**, cherchez ces lignes et remplacez les valeurs :

```env
# Trouvez cette ligne :
PENNYLANE_API_TOKEN=your_api_token_here

# Remplacez par (collez votre Token API REST) :
PENNYLANE_API_TOKEN=pk_live_abc123def456...

# -----

# Trouvez cette ligne :
PENNYLANE_DATA_SHARING_KEY=your_data_sharing_key_here

# Remplacez par (collez votre Data Sharing Key) :
PENNYLANE_DATA_SHARING_KEY=dsk_abc123def456...
```

**Enregistrez le fichier** : **Fichier** → **Enregistrer** (ou **Ctrl + S**)

**Fermez le Bloc-notes**.

✅ **C'est fait !** Vos clés sont maintenant configurées.

---

## 🚀 Étape 4 : Installer Penny (2 min)

**Retournez dans votre terminal PowerShell** (la fenêtre bleue).

**Tapez cette commande** :

```bash
pip install -r requirements.txt
```

**Puis appuyez sur Entrée**.

**Vous allez voir** plein de lignes défiler. **C'est normal !** Attendez que ça finisse (environ 1-2 minutes).

**Quand c'est fini**, vous voyez une ligne qui se termine par quelque chose comme :
```
Successfully installed ...
```

✅ **C'est bon !** Penny est maintenant installé.

---

## ▶️ Étape 5 : Démarrer le système (1 min)

**C'est la dernière étape !**

### 5.1 Démarrer Docker Compose

**Dans votre terminal**, tapez cette commande **magique** :

```bash
docker-compose up -d
```

**Puis appuyez sur Entrée**.

**Explication** : Cette commande démarre :
- La base de données PostgreSQL (où vos données seront stockées)
- Le scheduler automatique (qui synchronise toutes les 2 heures)

**Vous allez voir** plein de lignes comme :
```
Creating network "penny_default"...
Pulling postgres (postgres:15-alpine)...
...
Creating pennylane_postgres...
Creating pennylane_scheduler...
```

**Attendez environ 1 minute**. Quand c'est fini, vous retournez à une ligne de commande normale.

✅ **Félicitations !** Le système est maintenant lancé et tourne **en arrière-plan**.

---

### 5.2 Vérifier que tout fonctionne

**Dans votre terminal**, tapez :

```bash
docker-compose ps
```

**Puis appuyez sur Entrée**.

**Vous devez voir** :
```
NAME                  STATUS
pennylane_postgres    Up (healthy)
pennylane_pgadmin     Up
pennylane_scheduler   Up (healthy)
```

✅ **Si vous voyez "Up"** pour les 3 lignes : **Tout fonctionne parfaitement** !

---

### 5.3 Voir ce qui se passe

**Vous voulez voir le système travailler ?**

**Dans votre terminal**, tapez :

```bash
docker-compose logs scheduler -f
```

**Puis appuyez sur Entrée**.

**Vous allez voir en direct** :
```
[DEMARRAGE] Notebook Scheduler Pennylane
[SYNC] DEBUT synchronisation
[EXECUTE] Clients (API REST)
[OK] customers: 7 lignes exportées
[EXECUTE] Factures clients (API REST)
...
```

**C'est magnifique, non ?** 🎉

**Pour arrêter l'affichage** : Appuyez sur **Ctrl + C**

---

## 🎉 Étape 6 : Connecter Power BI (2 min)

**Maintenant que vos données sont synchronisées, on va les connecter à Power BI !**

### 6.1 Ouvrir Power BI Desktop

1. Lancez **Power BI Desktop**
2. Cliquez sur **Obtenir les données**
3. Cherchez **PostgreSQL** dans la liste
4. Cliquez sur **PostgreSQL** puis **Connecter**

---

### 6.2 Remplir les informations de connexion

**Une fenêtre s'ouvre.** Remplissez comme ceci :

| Champ | Valeur à saisir |
|-------|-----------------|
| **Serveur** | `localhost:5433` |
| **Base de données** | `pennylane_db` |

Cliquez sur **OK**.

---

### 6.3 Saisir vos identifiants

**Une nouvelle fenêtre demande les identifiants.**

| Champ | Valeur à saisir |
|-------|-----------------|
| **Nom d'utilisateur** | `pennylane_user` |
| **Mot de passe** | `Penny2025!SecurePass` |

Cliquez sur **Connecter**.

---

### 6.4 Sélectionner vos tables

**Vous voyez maintenant toutes vos tables Pennylane !**

1. **Cochez** les tables que vous voulez importer (par exemple : `customers`, `analytical_ledger`, `general_ledger`)
2. Cliquez sur **Charger**

**Patientez quelques secondes...**

✅ **Et voilà !** Vos données Pennylane sont maintenant dans Power BI !

**Bonus** : Ces données se **mettent à jour automatiquement toutes les 2 heures** grâce au scheduler !

---

## 📖 Utilisation quotidienne

### Redémarrer après un reboot du PC

**Si vous redémarrez votre ordinateur**, le système s'arrête. Pour le relancer :

1. **Ouvrez Docker Desktop** (il doit être lancé)
2. **Ouvrez PowerShell**
3. Tapez ces 2 commandes :
   ```bash
   cd C:\Users\VOTRE_NOM\Penny
   docker-compose up -d
   ```

**C'est tout !** Le système redémarre.

---

### Voir si le système tourne

**Pour vérifier que tout va bien** :

```bash
docker-compose ps
```

Vous devez voir "Up" pour les 3 services.

---

### Arrêter le système

**Si vous voulez arrêter le système** (par exemple, pour économiser des ressources) :

```bash
docker-compose down
```

**Pour le relancer** :

```bash
docker-compose up -d
```

---

## ❓ FAQ - Questions fréquentes

### 🔴 "Docker n'est pas lancé"

**Solution** : Ouvrez **Docker Desktop** depuis le menu Démarrer. Attendez que l'icône en bas à droite devienne verte.

---

### 🔴 "Port 5433 déjà utilisé"

**Solution** : Un autre programme utilise ce port. Modifiez le fichier `.env` :
```env
POSTGRES_PORT=5434
```

Puis relancez :
```bash
docker-compose down
docker-compose up -d
```

---

### 🔴 "Connexion Power BI refusée"

**Vérifiez** :
1. Docker Desktop est lancé ✅
2. Les 3 conteneurs sont "Up" (`docker-compose ps`) ✅
3. Vous utilisez bien `localhost:5433` ✅
4. Mot de passe correct : `Penny2025!SecurePass` ✅

---

### 🔴 "Mes données ne se mettent pas à jour"

**Le scheduler tourne toutes les 2 heures.**

**Pour forcer une mise à jour immédiate** :

```bash
docker-compose restart scheduler
```

---

## 🎓 Aller plus loin

### Voir toutes les commandes

Consultez le [GUIDE_AUTOMATION.md](GUIDE_AUTOMATION.md) pour des explications détaillées.

### Personnaliser vos transformations

Lisez le [README.md](README.md) pour apprendre à modifier les notebooks Jupyter et ajouter vos propres colonnes calculées.

### Dépannage avancé

Si vous avez un problème, lancez le diagnostic automatique :

```bash
python verify_setup.py
```

Ce script vérifie tous les composants et vous dit exactement ce qui ne va pas.

---

## 🎉 Conclusion

**Félicitations !** 🎊

Vous avez maintenant un système professionnel qui :
- ✅ Synchronise vos données Pennylane **automatiquement toutes les 2 heures**
- ✅ Les transforme et les stocke dans une **base de données PostgreSQL**
- ✅ Les rend disponibles pour **Power BI** en quelques secondes
- ✅ Tourne **en arrière-plan** sans intervention de votre part

**Vous pouvez maintenant créer vos tableaux de bord Power BI avec des données toujours à jour !**

---

## 💬 Besoin d'aide ?

- **Documentation complète** : [README.md](README.md)
- **Guide automatisation** : [GUIDE_AUTOMATION.md](GUIDE_AUTOMATION.md)
- **Issues GitHub** : [github.com/yves34690/Penny/issues](https://github.com/yves34690/Penny/issues)

**Bonne analyse de données ! 📊**

---

**Auteur** : Yves Cloarec
**Version** : 1.0
**Date** : Octobre 2025
