"""
Module de chargement de configuration depuis .env et config.json
Centralise la gestion des variables d'environnement
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Charger le fichier .env depuis la racine du projet
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)


def get_env(key: str, default: Any = None, required: bool = False) -> Any:
    """
    Récupère une variable d'environnement

    Args:
        key: Nom de la variable
        default: Valeur par défaut
        required: Si True, lève une erreur si la variable n'existe pas

    Returns:
        Valeur de la variable d'environnement
    """
    value = os.getenv(key, default)

    if required and value is None:
        raise ValueError(
            f"Variable d'environnement '{key}' requise mais non définie.\n"
            f"Vérifiez votre fichier .env (créer depuis .env.example si nécessaire)"
        )

    return value


def get_env_bool(key: str, default: bool = False) -> bool:
    """Récupère une variable d'environnement booléenne"""
    value = get_env(key, str(default))
    return value.lower() in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """Récupère une variable d'environnement entière"""
    value = get_env(key, str(default))
    try:
        return int(value)
    except ValueError:
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """Récupère une variable d'environnement flottante"""
    value = get_env(key, str(default))
    try:
        return float(value)
    except ValueError:
        return default


def load_full_config() -> Dict[str, Any]:
    """
    Charge la configuration complète depuis .env et config.json

    Returns:
        Dictionnaire de configuration complet
    """
    # Charger config.json (endpoints uniquement maintenant)
    config_path = project_root / 'config.json'

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}

    # Ajouter les configurations depuis .env
    config['pennylane_api'] = {
        'api_key': get_env('PENNYLANE_API_KEY', required=True),
        'base_url': get_env('PENNYLANE_BASE_URL', 'https://app.pennylane.com/api/external/v1'),
        'rate_limit': {
            'requests_per_second': get_env_float('PENNYLANE_RATE_LIMIT', 4.5)
        }
    }

    config['database'] = {
        'host': get_env('POSTGRES_HOST', 'localhost'),
        'port': get_env_int('POSTGRES_PORT', 5432),
        'database': get_env('POSTGRES_DB', 'pennylane_data'),
        'user': get_env('POSTGRES_USER', 'pennylane_user'),
        'password': get_env('POSTGRES_PASSWORD', required=True),
        'schema': get_env('POSTGRES_SCHEMA', 'pennylane')
    }

    config['scheduler'] = {
        'enabled': get_env_bool('SCHEDULER_ENABLED', True),
        'interval_minutes': get_env_int('SCHEDULER_INTERVAL_MINUTES', 10)
    }

    config['logging'] = {
        'level': get_env('LOG_LEVEL', 'INFO'),
        'file': get_env('LOG_FILE', 'logs/pennylane_etl.log'),
        'max_bytes': get_env_int('LOG_MAX_BYTES', 10485760),
        'backup_count': get_env_int('LOG_BACKUP_COUNT', 5)
    }

    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Valide que la configuration est complète

    Args:
        config: Configuration à valider

    Returns:
        True si valide

    Raises:
        ValueError: Si configuration invalide
    """
    required_keys = ['pennylane_api', 'database', 'endpoints']

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Configuration incomplète: section '{key}' manquante")

    # Vérifier que l'API key n'est pas la valeur par défaut
    api_key = config['pennylane_api']['api_key']
    if not api_key or 'VOTRE' in api_key.upper() or 'ICI' in api_key.upper():
        raise ValueError(
            "Clé API Pennylane invalide.\n"
            "Configurez PENNYLANE_API_KEY dans votre fichier .env"
        )

    # Vérifier que le mot de passe PostgreSQL n'est pas par défaut
    db_password = config['database']['password']
    if not db_password or 'changeme' in db_password.lower():
        raise ValueError(
            "Mot de passe PostgreSQL invalide.\n"
            "Configurez POSTGRES_PASSWORD dans votre fichier .env"
        )

    return True


# Export des fonctions principales
__all__ = [
    'load_full_config',
    'validate_config',
    'get_env',
    'get_env_bool',
    'get_env_int',
    'get_env_float'
]
