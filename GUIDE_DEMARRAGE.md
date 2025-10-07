# 🚀 Guide de démarrage rapide

## Étapes à suivre MAINTENANT

### 1. ✅ Installation des dépendances Python

```bash
cd c:\Penny
pip install -r requirements.txt
```

### 2. ✅ Configuration de votre clé API Pennylane

Ouvrir [config.json](config.json) et remplacer :

```json
"api_key": "VOTRE_CLE_API_ICI"
```

Par votre vraie clé API Pennylane.

### 3. ✅ Démarrer PostgreSQL avec Docker

```bash
docker-compose up -d
```

Vérifier que ça fonctionne :

```bash
docker ps
```

Vous devriez voir 2 conteneurs : `pennylane_postgres` et `pennylane_pgadmin`.

### 4. ✅ Tester la connexion API et première extraction

```bash
cd src
python main.py full
```

Cette commande va :
- Tester la connexion à l'API Pennylane
- Extraire TOUTES les données de tous les endpoints configurés
- Les charger dans PostgreSQL
- Afficher un résumé

⏱ **Durée estimée** : 5-30 minutes selon le volume de données.

### 5. ✅ Vérifier les données dans PostgreSQL

Ouvrir pgAdmin : [http://localhost:5050](http://localhost:5050)

- Email : `admin@pennylane.local`
- Password : `admin`

Ou avec une requête SQL directe :

```bash
docker exec -it pennylane_postgres psql -U pennylane_user -d pennylane_data -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'pennylane';"
```

### 6. ✅ Créer votre Jupyter Notebook pour transformations

Créer un fichier `transformations.ipynb` :

```python
import pandas as pd
from sqlalchemy import create_engine

# Connexion PostgreSQL
engine = create_engine('postgresql://pennylane_user:changeme_secure_password@localhost:5432/pennylane_data')

# Charger une table
df = pd.read_sql('SELECT * FROM pennylane.invoices', engine)

# FAITES VOS TRANSFORMATIONS ICI
# Exemple : ajouter colonne montant HT en euros
df['montant_ht_euros'] = df['amount_cents'] / 100

# Sauvegarder dans nouvelle table
df.to_sql('invoices_clean', engine, schema='pennylane', if_exists='replace', index=False)

print(f"✓ {len(df)} factures transformées")
```

### 7. ✅ Connecter Power BI

1. Power BI Desktop → **Obtenir des données** → **PostgreSQL**
2. Serveur : `localhost`, Base : `pennylane_data`
3. Sélectionner les tables du schéma `pennylane`
4. Importer (pas DirectQuery)

### 8. ✅ Activer le planificateur automatique (10 min)

```bash
cd src
python scheduler.py
```

Le script s'exécutera toutes les 10 minutes automatiquement.

## 🎯 Workflow complet

```
1. Planificateur Python (toutes les 10 min)
   └─> Extrait API Pennylane
   └─> Charge dans PostgreSQL (tables brutes)

2. Jupyter Notebook (à votre rythme)
   └─> Lit tables brutes PostgreSQL
   └─> Applique VOS transformations métier
   └─> Écrit tables transformées PostgreSQL

3. Power BI
   └─> Se connecte aux tables transformées PostgreSQL
   └─> Actualisation rapide (données déjà prêtes)
```

## ❓ Questions fréquentes

### Où sont mes données ?

Dans PostgreSQL, schéma `pennylane`, accessible :
- Via pgAdmin : [http://localhost:5050](http://localhost:5050)
- Via Python/Jupyter
- Via Power BI

### Comment arrêter PostgreSQL ?

```bash
docker-compose down
```

### Comment voir les logs ?

```bash
type logs\pennylane_etl.log
```

### Je veux changer l'intervalle d'actualisation

Modifier `config.json` :

```json
"scheduler": {
  "interval_minutes": 5  // Au lieu de 10
}
```

### Quels endpoints sont synchronisés ?

Voir la section `endpoints.enabled` dans [config.json](config.json).

Pour ajouter/retirer un endpoint, modifier cette section.

---

**Prêt ? Lancez l'étape 1 ! 🚀**
