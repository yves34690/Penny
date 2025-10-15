# 🎓 Guide pour Débutants Complets

**Bienvenue !** Ce guide est conçu pour vous accompagner pas à pas, même si vous n'avez **jamais codé** de votre vie.

---

## 📚 Table des matières

1. [C'est quoi ce projet ?](#1-cest-quoi-ce-projet-)
2. [De quoi ai-je besoin ?](#2-de-quoi-ai-je-besoin-)
3. [Installation pas à pas](#3-installation-pas-à-pas)
4. [Votre première utilisation](#4-votre-première-utilisation)
5. [Personnaliser vos données](#5-personnaliser-vos-données)
6. [Questions fréquentes](#6-questions-fréquentes)
7. [Glossaire](#7-glossaire)

---

## 1. C'est quoi ce projet ? 🤔

### En une phrase
**Ce projet récupère automatiquement vos données Pennylane et les prépare pour Power BI.**

### Plus en détail

Imaginons que vous êtes expert-comptable ou DAF. Vous utilisez :
- **Pennylane** : Pour la comptabilité
- **Power BI** : Pour faire des tableaux de bord

**Le problème** :
- Vous devez exporter manuellement les données depuis Pennylane
- Les transformations sont compliquées dans Power BI
- Vous perdez du temps à rafraîchir

**La solution (ce projet)** :
- ✅ Récupère automatiquement vos données Pennylane
- ✅ Les transforme selon vos besoins
- ✅ Les met dans une base de données PostgreSQL
- ✅ Power BI peut s'y connecter directement

**Résultat** : Vos tableaux de bord Power BI se mettent à jour automatiquement toutes les 2 heures ! 🎉

---

## 2. De quoi ai-je besoin ? 📦

### Prérequis obligatoires

#### 🔐 Accès Pennylane
- Un compte Pennylane (logique !)
- Token API de développeur ([comment l'obtenir](#obtenir-votre-token-pennylane))

#### 💻 Logiciels à installer
Pas de panique, je vais tout vous expliquer !

| Logiciel | À quoi ça sert ? | Téléchargement |
|----------|------------------|----------------|
| **Python 3.12** | Le "moteur" qui fait tourner le projet | [python.org](https://www.python.org/downloads/) |
| **Docker Desktop** | Installe automatiquement PostgreSQL | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Git** | Télécharge le projet depuis GitHub | [git-scm.com](https://git-scm.com/downloads) |
| **Visual Studio Code** (optionnel) | Éditeur de code user-friendly | [code.visualstudio.com](https://code.visualstudio.com/) |

---

## 3. Installation pas à pas 🚀

### Étape 1 : Installer Python

1. **Télécharger Python 3.12** : [Cliquez ici](https://www.python.org/downloads/)
2. **Lancer l'installateur**
3. ⚠️ **IMPORTANT** : Cochez **"Add Python to PATH"** en bas de la fenêtre !
4. Cliquer sur **"Install Now"**
5. Attendre la fin de l'installation

**Vérifier que ça marche** :
```bash
# Ouvrir "Invite de commandes" (Windows) ou "Terminal" (Mac)
python --version
```
Vous devriez voir : `Python 3.12.x`

---

### Étape 2 : Installer Docker Desktop

1. **Télécharger Docker** : [Cliquez ici](https://www.docker.com/products/docker-desktop/)
2. **Installer** en suivant les instructions
3. **Redémarrer votre ordinateur** (oui, c'est obligatoire !)
4. **Lancer Docker Desktop**

**Vérifier que ça marche** :
```bash
docker --version
```
Vous devriez voir : `Docker version 20.x.x`

---

### Étape 3 : Télécharger le projet

#### Option A : Avec Git (recommandé)

```bash
# Ouvrir votre terminal
cd Documents
git clone https://github.com/votre-username/Penny.git
cd Penny
```

#### Option B : Sans Git (manuel)

1. Aller sur [GitHub - Penny](https://github.com/votre-username/Penny)
2. Cliquer sur **"Code"** (bouton vert)
3. Cliquer sur **"Download ZIP"**
4. Extraire le ZIP dans vos Documents
5. Ouvrir le dossier `Penny`

---

### Étape 4 : Configurer vos identifiants Pennylane

#### Obtenir votre token Pennylane

1. **Connexion Pennylane** : [app.pennylane.com](https://app.pennylane.com)
2. Aller dans **Paramètres** → **Développeurs**
3. Cliquer sur **"Créer un token"**
4. **Copier le token** (gardez-le précieusement !)

#### Créer votre fichier `.env`

1. Dans le dossier `Penny`, trouver le fichier `.env.example`
2. **Copier-coller** ce fichier
3. **Renommer la copie** en `.env` (sans "example")
4. **Ouvrir `.env`** avec Bloc-notes (Windows) ou TextEdit (Mac)
5. **Remplacer** les valeurs entre guillemets :

```env
# Avant (exemple)
PENNYLANE_API_TOKEN="VOTRE_TOKEN_ICI"

# Après (avec VOTRE token)
PENNYLANE_API_TOKEN="aHcC1umL5l4IlC5U8trWo5v8lHrYJHQMvDDdGWTrC2Q"
```

**⚠️ ATTENTION** : Ne partagez JAMAIS ce fichier `.env` sur Internet !

---

### Étape 5 : Installer les dépendances Python

**Qu'est-ce qu'une dépendance ?**
Ce sont des "outils" Python dont le projet a besoin pour fonctionner.

```bash
# Dans votre terminal, dossier Penny
pip install -r requirements.txt
```

**Attendre** que tout s'installe (2-3 minutes).

Vous verrez défiler plein de lignes, c'est normal ! ✅

---

### Étape 6 : Démarrer PostgreSQL

**Qu'est-ce que PostgreSQL ?**
C'est la "boîte" où vos données Pennylane seront stockées.

```bash
docker-compose up -d
```

**Vérifier que ça marche** :
```bash
docker ps
```

Vous devriez voir 2 conteneurs :
- `postgres`
- `pgadmin`

---

## 4. Votre première utilisation 🎉

### Étape 1 : Tester un notebook manuellement

1. **Lancer Jupyter** :
```bash
jupyter notebook
```

Une fenêtre s'ouvre dans votre navigateur.

2. **Naviguer** vers `data/API Publique/`

3. **Ouvrir** `Import_customers.ipynb`

4. **Exécuter toutes les cellules** :
   - Menu : `Cell` → `Run All`

5. **Voir les résultats** ! 🎉

Vous devriez voir s'afficher vos clients Pennylane.

---

### Étape 2 : Automatiser avec le scheduler

Une fois que vous avez testé et que tout fonctionne :

```bash
python src/notebook_scheduler.py
```

**Ce qui se passe** :
- Le programme récupère vos données Pennylane
- Il exécute tous vos notebooks automatiquement
- Il exporte dans PostgreSQL
- **Toutes les 2 heures**, ça recommence automatiquement !

**Pour arrêter** : `Ctrl + C`

---

### Étape 3 : Connecter Power BI

1. **Ouvrir Power BI Desktop**

2. **Obtenir les données** → **PostgreSQL**

3. **Entrer les informations** :
   - **Serveur** : `localhost:5433`
   - **Base de données** : `pennylane_db`

4. **Se connecter** :
   - Utilisateur : `pennylane_user`
   - Mot de passe : (celui de votre `.env`)

5. **Sélectionner les tables** :
   - Schema : `pennylane`
   - Cocher les tables souhaitées

6. **Charger** → **C'est prêt !** 🎉

---

## 5. Personnaliser vos données 🎨

### Exemple concret : Ajouter une colonne

**Contexte** : Vous voulez ajouter une colonne "Région" basée sur le code postal de vos clients.

#### Étape 1 : Ouvrir le notebook

```bash
jupyter notebook
```

Ouvrir : `data/API Publique/Import_customers.ipynb`

#### Étape 2 : Trouver la cellule de transformations

Cherchez une cellule avec du code qui ressemble à :

```python
# Cellule existante
df['billing_address'] = ...
```

#### Étape 3 : Ajouter votre transformation

**Juste après**, ajouter une nouvelle cellule (`+` dans la barre d'outils) :

```python
# Déterminer la région selon le code postal
def determiner_region(code_postal):
    if code_postal.startswith('75'):
        return 'Île-de-France'
    elif code_postal.startswith('13'):
        return 'Provence'
    elif code_postal.startswith('69'):
        return 'Auvergne-Rhône-Alpes'
    else:
        return 'Autre'

# Appliquer à toutes les lignes
df['Region'] = df['billing_postal_code'].apply(determiner_region)

# Voir le résultat
display(df[['name', 'billing_postal_code', 'Region']].head())
```

#### Étape 4 : Tester

1. **Exécuter la cellule** (`Shift + Entrée`)
2. **Vérifier** que la colonne "Region" apparaît
3. **Corriger** si besoin

#### Étape 5 : Sauvegarder

1. Menu : `File` → `Save`
2. **C'est tout !**

**Magie** : La prochaine fois que le scheduler tourne, votre colonne "Region" sera automatiquement appliquée ! ✨

---

### Autres exemples de personnalisation

#### Calculer un délai de paiement

**Notebook** : `Import_customer_invoices.ipynb`

```python
# Convertir les dates
df['date'] = pd.to_datetime(df['date'])
df['deadline'] = pd.to_datetime(df['deadline'])

# Calculer le délai
df['Delai_Paiement_Jours'] = (df['deadline'] - df['date']).dt.days

# Marquer les retards
df['En_Retard'] = df['Delai_Paiement_Jours'] < 0
```

#### Classifier les comptes comptables

**Notebook** : `Import_analytical_ledger.ipynb`

```python
# Fonction de classification
def classifier_compte(numero):
    premier_chiffre = str(numero)[0]

    if premier_chiffre == '6':
        return 'Charges'
    elif premier_chiffre == '7':
        return 'Produits'
    elif premier_chiffre == '1':
        return 'Capitaux'
    elif premier_chiffre == '2':
        return 'Immobilisations'
    else:
        return 'Autre'

df['Type_Compte'] = df['plan_item_number'].apply(classifier_compte)
```

#### Ajouter un indicateur métier

**Notebook** : `Import_supplier_invoices.ipynb`

```python
# Identifier les grosses dépenses
df['Depense_Importante'] = df['amount'] > 5000

# Compter par fournisseur
grosses_depenses = df[df['Depense_Importante']].groupby('supplier_name').size()
```

---

## 6. Questions fréquentes ❓

### "Je ne comprends rien au code, c'est normal ?"

**Oui, totalement normal !** Vous n'avez pas besoin de tout comprendre.

**Ce que vous devez savoir** :
- Où modifier vos transformations (dans les notebooks)
- Comment copier-coller des exemples
- Comment tester si ça marche

**Le reste**, le programme s'en occupe automatiquement !

---

### "J'ai une erreur, que faire ?"

**Pas de panique !** Les erreurs font partie du processus.

**Étapes de dépannage** :

1. **Lire le message d'erreur**
   - Il est souvent en anglais
   - Cherchez des mots-clés (ex: "FileNotFoundError" = fichier introuvable)

2. **Google est votre ami**
   - Copiez le message d'erreur dans Google
   - Ajoutez "python" ou "jupyter notebook"

3. **Vérifier les bases**
   - Votre fichier `.env` est correct ?
   - Docker tourne-t-il ?
   - Internet fonctionne ?

4. **Consulter les logs**
```bash
# Voir les logs du scheduler
Get-Content logs\notebook_scheduler.log
```

5. **Demander de l'aide**
   - Ouvrir une issue sur GitHub
   - Forum Pennylane
   - Communauté Python

---

### "Comment je fais si je veux changer la fréquence ?"

**Objectif** : Au lieu de 2h, lancer toutes les heures.

1. **Ouvrir** `src/notebook_scheduler.py` avec un éditeur de texte

2. **Chercher** (Ctrl+F) : `schedule.every(2).hours`

3. **Remplacer** par : `schedule.every(1).hours`

4. **Sauvegarder**

5. **Relancer** le scheduler

**Exemples d'autres fréquences** :
```python
schedule.every(30).minutes.do(...)  # Toutes les 30 min
schedule.every().day.at("08:00").do(...)  # Tous les jours à 8h
schedule.every().monday.do(...)  # Tous les lundis
```

---

### "Où sont stockées mes données ?"

**2 endroits** :

1. **PostgreSQL** (la base de données)
   - Host : `localhost:5433`
   - Accessible via pgAdmin : [http://localhost:5050](http://localhost:5050)

2. **Notebooks exécutés** (l'historique)
   - Dossier : `data/outputs/`
   - Fichiers : `analytical_ledger_20251015_123045.ipynb`

---

### "C'est sécurisé ?"

**Oui**, mais à condition de :

✅ **NE JAMAIS partager** votre fichier `.env`
✅ **NE JAMAIS commiter** `.env` sur GitHub
✅ Utiliser un **mot de passe fort** pour PostgreSQL
✅ Ne pas exposer PostgreSQL sur Internet (rester en `localhost`)

**Le fichier `.gitignore`** empêche automatiquement `.env` d'être uploadé.

---

### "Ça coûte de l'argent ?"

**Non !** Tout est gratuit :
- Python : Gratuit et open-source
- Docker : Version gratuite suffisante
- PostgreSQL : Gratuit
- Ce projet : Open-source gratuit

**Seul coût potentiel** : Pennylane (mais vous l'avez déjà !)

---

## 7. Glossaire 📖

### Termes techniques expliqués simplement

| Terme | Explication simple | Analogie |
|-------|-------------------|----------|
| **API** | Moyen pour 2 logiciels de communiquer | Comme un serveur qui prend votre commande au restaurant |
| **Token** | Mot de passe pour accéder à l'API | Comme un badge d'entrée |
| **PostgreSQL** | Base de données (stocke vos données) | Comme un classeur géant bien organisé |
| **Docker** | Permet d'installer PostgreSQL facilement | Comme une machine à café capsules : facile à utiliser |
| **Jupyter Notebook** | Document interactif mêlant texte et code | Comme un cahier où vous pouvez exécuter des calculs |
| **Scheduler** | Programme qui automatise des tâches répétitives | Comme un réveil qui sonne tous les jours |
| **Pandas** | Librairie Python pour manipuler des données | Comme Excel mais en code |
| **DataFrame** | Tableau de données (lignes/colonnes) | Exactement comme une feuille Excel |
| **Kernel** | "Moteur" qui exécute votre code Python | Comme le processeur de votre ordinateur |
| **Repository (Repo)** | Projet hébergé sur GitHub | Comme un dossier partagé en ligne |
| **Fork** | Copie d'un projet GitHub pour le personnaliser | Comme photocopier un livre pour l'annoter |
| **Pull Request** | Proposition de modification à un projet | Comme suggérer une correction à l'auteur d'un livre |

---

## 8. Ressources pour aller plus loin 📚

### Apprendre Python (débutant)

- **Codecademy** : [Learn Python 3](https://www.codecademy.com/learn/learn-python-3) (Gratuit)
- **OpenClassrooms** : [Apprenez les bases de Python](https://openclassrooms.com/fr/courses/7168871-apprenez-les-bases-du-langage-python) (Français, gratuit)
- **YouTube** : Cherchez "Python pour débutants français"

### Apprendre Pandas (manipulation de données)

- **Pandas Documentation** : [Getting Started](https://pandas.pydata.org/docs/getting_started/index.html) (Anglais)
- **YouTube** : "Pandas tutorial français"

### Comprendre Jupyter Notebooks

- **Documentation officielle** : [Jupyter Notebook Basics](https://jupyter-notebook.readthedocs.io/en/stable/notebook.html)
- **YouTube** : "Jupyter notebook tutorial français"

### Communauté Pennylane

- **Forum** : [community.pennylane.com](https://community.pennylane.com)
- **Documentation API** : [pennylane.readme.io](https://pennylane.readme.io)

---

## 9. Checklist de démarrage ✅

Avant de commencer, vérifiez que vous avez :

- [ ] Python 3.12 installé
- [ ] Docker Desktop installé et démarré
- [ ] Projet téléchargé (Git ou ZIP)
- [ ] Fichier `.env` créé et configuré avec votre token
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] PostgreSQL démarré (`docker-compose up -d`)
- [ ] Test d'un notebook réussi (Jupyter)
- [ ] Scheduler lancé et fonctionnel

**Si tout est coché, vous êtes prêt ! 🚀**

---

## 10. Contact et support 💬

### Besoin d'aide ?

1. **GitHub Issues** : [Poser une question](https://github.com/votre-username/Penny/issues)
2. **Forum Pennylane** : [community.pennylane.com](https://community.pennylane.com)
3. **Documentation** :
   - [README principal](README.md)
   - [Guide scheduler notebooks](README_NOTEBOOK_SCHEDULER.md)
   - [Choix du scheduler](CHOIX_SCHEDULER.md)

### Contribuer au projet

Vous avez amélioré quelque chose ? Partagez !
- Fork le projet
- Faites vos modifications
- Soumettez une Pull Request

**Tous les niveaux sont bienvenus !** 🤝

---

## 🎉 Félicitations !

Vous êtes maintenant prêt à utiliser ce projet pour automatiser vos données Pennylane !

**Prochain objectif** : Personnaliser vos premiers notebooks 🚀

---

**Questions ? N'hésitez pas à ouvrir une issue sur GitHub !**

*Document créé avec ❤️ pour la communauté Pennylane*
