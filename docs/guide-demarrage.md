# Guide de démarrage rapide

Ce guide vous permettra d'installer et configurer Penny en moins de 10 minutes.

## Prérequis

Avant de commencer, assurez-vous d'avoir :

- [x] Python 3.12 ou supérieur
- [x] Docker Desktop installé et démarré
- [x] Une clé API Pennylane (Premium + Module comptable)
- [x] Git installé

## Installation

### Étape 1 : Cloner le dépôt

```bash
git clone https://github.com/yves34690/Penny.git
cd Penny
```

### Étape 2 : Configurer les secrets

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos valeurs
notepad .env  # Windows
nano .env     # Linux/Mac
```

!!! warning "Variables obligatoires"
    Vous DEVEZ configurer au minimum :

    - `PENNYLANE_API_KEY` : Votre clé API Pennylane
    - `POSTGRES_PASSWORD` : Un mot de passe sécurisé

### Étape 3 : Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 4 : Démarrer PostgreSQL

```bash
docker-compose up -d
```

Vérifiez que tout fonctionne :

```bash
docker ps
```

Vous devriez voir 2 conteneurs actifs :
- `pennylane_postgres`
- `pennylane_pgadmin`

### Étape 5 : Première extraction

```bash
cd src
python main.py full
```

!!! success "Succès !"
    Si vous voyez `✓ Configuration chargée et validée`, tout fonctionne !

## Vérification

### Accéder à pgAdmin

Ouvrez [http://localhost:5050](http://localhost:5050)

- Email : `admin@pennylane.local`
- Password : `admin`

### Consulter les données

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'pennylane';
```

## Prochaines étapes

- [Guide utilisateur complet](guide-utilisateur.md)
- [Configuration avancée](configuration.md)
- [Connexion Power BI](guide-utilisateur.md#connexion-power-bi)
