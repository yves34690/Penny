# FAQ (Questions fréquentes)

## Questions générales

### Penny est-il gratuit ?

Oui, Penny est open-source sous licence MIT. Gratuit pour usage personnel et commercial.

### Quels sont les prérequis ?

- Compte Pennylane Premium + Module comptable
- Python 3.12+
- Docker Desktop
- Clé API Pennylane

### Fonctionne-t-il sur Mac/Linux ?

Oui, compatible Windows, macOS et Linux.

## Installation

### L'installation prend combien de temps ?

Environ 10 minutes pour installation complète :
- 2 min : Clone + dépendances Python
- 3 min : Configuration .env
- 5 min : Docker + première extraction

### Puis-je utiliser sans Docker ?

Non recommandé. PostgreSQL via Docker simplifie installation et garantit compatibilité.

Alternative : Installer PostgreSQL nativement et adapter `config.json`.

## Configuration

### Comment obtenir ma clé API Pennylane ?

1. [app.pennylane.com](https://app.pennylane.com)
2. **Paramètres** → **API**
3. **Générer une clé API**
4. Copier dans `.env`

### Puis-je utiliser plusieurs clés API ?

Oui, pour multi-comptes :

```env
# .env pour client A
PENNYLANE_API_KEY=cle_client_a
POSTGRES_DB=client_a_data
```

Dupliquer projet ou changer `.env` entre exécutions.

### Comment changer l'intervalle d'actualisation ?

```env
# .env - Actualisation toutes les 5 minutes
SCHEDULER_INTERVAL_MINUTES=5
```

## Utilisation

### Dois-je laisser le planificateur tourner en continu ?

**Recommandé** : Oui, pour actualisation temps réel.

**Alternative** : Exécution manuelle ou via cron/Task Scheduler.

### Puis-je arrêter pendant une extraction ?

Oui (`Ctrl+C`). L'extraction sera reprise à la prochaine exécution (mode incrémentiel).

### Que se passe-t-il si mon PC s'éteint ?

Aucun problème. Données PostgreSQL sauvegardées. Relancer après redémarrage.

### Comment savoir si l'extraction fonctionne ?

```bash
# Logs temps réel
tail -f logs/pennylane_etl.log

# Logs PostgreSQL
SELECT * FROM pennylane.etl_logs
ORDER BY execution_date DESC LIMIT 10;
```

## Performance

### Combien de temps pour première extraction ?

Dépend du volume :
- < 10k lignes : 1-2 min
- 100k lignes : 5-10 min
- 1M lignes : 30-60 min

### L'actualisation incrémentielle est plus rapide ?

Oui, **beaucoup plus rapide** :
- Complète : 30 min
- Incrémentielle : 30 sec (si peu de changements)

### Mon Power BI est toujours lent

Vérifiez :
1. Connexion en mode **Import** (pas DirectQuery)
2. Transformations dans **Jupyter** (pas Power Query)
3. Tables **indexées** dans PostgreSQL

## Données

### Quels endpoints sont synchronisés ?

Par défaut :
- Factures clients/fournisseurs
- Clients/Fournisseurs
- Transactions bancaires
- Écritures comptables
- Plan comptable
- Catégories

Modifiable dans `config.json`.

### Puis-je synchroniser seulement certaines tables ?

Oui, éditer `config.json` et retirer endpoints non désirés.

### Les données sont-elles historisées ?

Non par défaut (dernière version uniquement).

Pour historisation, implémenter :
```sql
CREATE TABLE pennylane.invoices_history (
    -- même structure + colonne version/date
);
```

### Comment supprimer toutes les données ?

```bash
docker-compose down -v  # -v supprime volumes
docker-compose up -d
```

## Sécurité

### Mes données sont-elles sécurisées ?

- ✅ Données stockées **localement** (votre machine)
- ✅ Pas de cloud tiers
- ✅ Secrets dans `.env` (non committé)
- ✅ PostgreSQL avec mot de passe

### Puis-je partager mon dépôt ?

Oui, mais :
- ❌ **JAMAIS** commiter `.env`
- ✅ Partager `.env.example`
- ✅ Chacun configure son `.env`

### Le mot de passe PostgreSQL est-il important ?

Localement : moins critique
Serveur : **très important** (accès réseau)

## Power BI

### Comment connecter Power BI ?

**Obtenir les données** → **PostgreSQL**
- Serveur : `localhost`
- Base : `pennylane_data`
- Mode : **Import**

### DirectQuery ou Import ?

**Import** recommandé pour :
- Performance
- Gros volumes
- Transformations complexes

### Actualisation Power BI

1. **Desktop** : Bouton Actualiser
2. **Service** : Planifier actualisation (ex: toutes les heures)

Données Penny actualisées toutes les 10 min → Power BI toujours quasi à jour !

## Dépannage

### "Variable PENNYLANE_API_KEY requise"

Créer fichier `.env` depuis `.env.example` et configurer.

### "Erreur connexion PostgreSQL"

```bash
docker ps  # Vérifier conteneur actif
docker-compose restart postgres
```

### "Aucune donnée extraite"

```bash
# Forcer extraction complète
python main.py full
```

### Autres problèmes ?

Voir [guide de dépannage](depannage.md).

## Évolutions

### Nouvelles fonctionnalités prévues ?

Voir [roadmap dans guide utilisateur](guide-utilisateur.md#évolutions-futures).

### Puis-je contribuer ?

Oui ! Pull requests bienvenues sur [GitHub](https://github.com/yves34690/Penny).

### Comment demander une fonctionnalité ?

[Créer une issue](https://github.com/yves34690/Penny/issues) avec label "enhancement".

## Support

### Où trouver de l'aide ?

1. Cette documentation
2. [Issues GitHub](https://github.com/yves34690/Penny/issues)
3. [Documentation Pennylane](https://pennylane.readme.io/)

### Puis-je contacter directement ?

Via issues GitHub (réponse sous 24-48h).

## Licence

### Puis-je utiliser commercialement ?

Oui, licence MIT = usage libre (personnel et commercial).

### Puis-je revendre Penny ?

Oui, mais :
- Mentionner licence MIT
- Créditer auteur original
- Open-source (pas propriétaire)
