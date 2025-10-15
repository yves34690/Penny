#!/usr/bin/env python3
"""
Script de vérification de la configuration Penny ETL
Vérifie que tous les composants sont correctement configurés

Usage:
    python verify_setup.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Couleurs pour Windows/Linux
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
except ImportError:
    GREEN = RED = YELLOW = BLUE = RESET = ''

def print_header(text):
    """Affiche un en-tête"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    """Affiche un message de succès"""
    print(f"{GREEN}[OK] {text}{RESET}")

def print_error(text):
    """Affiche un message d'erreur"""
    print(f"{RED}[ERREUR] {text}{RESET}")

def print_warning(text):
    """Affiche un avertissement"""
    print(f"{YELLOW}[ATTENTION] {text}{RESET}")

def print_info(text):
    """Affiche une information"""
    print(f"  {text}")

def check_env_file():
    """Vérifie l'existence du fichier .env"""
    print_header("1. VÉRIFICATION FICHIER .env")

    env_path = Path('.env')
    if not env_path.exists():
        print_error("Fichier .env non trouvé !")
        print_info("Créez-le depuis .env.example : cp .env.example .env")
        return False

    print_success("Fichier .env trouvé")
    return True

def check_env_variables():
    """Vérifie les variables d'environnement"""
    print_header("2. VÉRIFICATION VARIABLES D'ENVIRONNEMENT")

    load_dotenv()

    required_vars = {
        'Pennylane API REST': [
            'PENNYLANE_API_TOKEN',
            'PENNYLANE_API_BASE_URL'
        ],
        'Pennylane Redshift': [
            'PENNYLANE_DATA_SHARING_KEY',
            'REDSHIFT_HOST',
            'REDSHIFT_PORT',
            'REDSHIFT_DATABASE',
            'REDSHIFT_USER'
        ],
        'PostgreSQL Local': [
            'POSTGRES_HOST',
            'POSTGRES_PORT',
            'POSTGRES_DB',
            'POSTGRES_USER',
            'POSTGRES_PASSWORD'
        ]
    }

    all_ok = True
    for category, vars_list in required_vars.items():
        print(f"\n{YELLOW}{category}:{RESET}")
        for var in vars_list:
            value = os.getenv(var)
            if value and value != f'votre_{var.lower()}':
                # Masquer les secrets
                if 'PASSWORD' in var or 'KEY' in var or 'TOKEN' in var:
                    display_value = value[:8] + '...' if len(value) > 8 else '***'
                else:
                    display_value = value
                print_success(f"{var} = {display_value}")
            else:
                print_error(f"{var} non défini ou valeur par défaut")
                all_ok = False

    return all_ok

def check_docker():
    """Vérifie que Docker est démarré"""
    print_header("3. VÉRIFICATION DOCKER")

    import subprocess

    try:
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            # Vérifier si les conteneurs Penny tournent
            if 'pennylane_postgres' in result.stdout:
                print_success("PostgreSQL est démarré")
            else:
                print_warning("PostgreSQL non démarré")
                print_info("Lancez : docker-compose up -d")

            if 'pennylane_pgadmin' in result.stdout:
                print_success("pgAdmin est démarré")
            else:
                print_warning("pgAdmin non démarré (optionnel)")

            return True
        else:
            print_error("Docker n'est pas démarré")
            print_info("Démarrez Docker Desktop")
            return False

    except FileNotFoundError:
        print_error("Docker non installé")
        print_info("Installez Docker Desktop : https://www.docker.com/products/docker-desktop")
        return False
    except Exception as e:
        print_error(f"Erreur vérification Docker : {e}")
        return False

def check_postgresql_connection():
    """Vérifie la connexion PostgreSQL"""
    print_header("4. VÉRIFICATION CONNEXION POSTGRESQL")

    try:
        import psycopg2

        load_dotenv()

        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]

        print_success(f"Connexion PostgreSQL OK")
        print_info(f"Version : {version.split(',')[0]}")

        # Vérifier schéma
        cursor.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'pennylane'"
        )
        if cursor.fetchone():
            print_success("Schéma 'pennylane' existe")
        else:
            print_warning("Schéma 'pennylane' n'existe pas encore")
            print_info("Il sera créé lors de la première synchronisation")

        cursor.close()
        conn.close()

        return True

    except ImportError:
        print_error("Module psycopg2 non installé")
        print_info("Installez : pip install -r requirements.txt")
        return False
    except Exception as e:
        print_error(f"Connexion échouée : {e}")
        print_info("Vérifiez que PostgreSQL est démarré : docker-compose up -d")
        return False

def check_redshift_connection():
    """Vérifie la connexion Redshift"""
    print_header("5. VÉRIFICATION CONNEXION REDSHIFT")

    try:
        import psycopg2

        load_dotenv()

        conn = psycopg2.connect(
            host=os.getenv('REDSHIFT_HOST'),
            port=os.getenv('REDSHIFT_PORT'),
            database=os.getenv('REDSHIFT_DATABASE'),
            user=os.getenv('REDSHIFT_USER'),
            password=os.getenv('REDSHIFT_PASSWORD')
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]

        print_success(f"Connexion Redshift OK")
        print_info(f"Version : {version.split()[0]}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print_error(f"Connexion Redshift échouée : {e}")
        print_info("Vérifiez PENNYLANE_DATA_SHARING_KEY dans .env")
        return False

def check_python_packages():
    """Vérifie les packages Python"""
    print_header("6. VÉRIFICATION PACKAGES PYTHON")

    required_packages = [
        ('pandas', 'pandas'),
        ('psycopg2', 'psycopg2'),
        ('python-dotenv', 'dotenv'),
        ('requests', 'requests'),
        ('schedule', 'schedule'),
        ('papermill', 'papermill'),
        ('nbformat', 'nbformat'),
        ('nbconvert', 'nbconvert')
    ]

    all_ok = True
    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
            print_success(f"{display_name} installé")
        except ImportError:
            print_error(f"{display_name} non installé")
            all_ok = False

    if not all_ok:
        print_info("\nInstallez les packages manquants : pip install -r requirements.txt")

    return all_ok

def check_notebooks():
    """Vérifie les notebooks"""
    print_header("7. VÉRIFICATION NOTEBOOKS")

    notebooks_dir = Path('data/API Publique')

    if not notebooks_dir.exists():
        print_error("Dossier 'data/API Publique' non trouvé")
        return False

    notebooks = list(notebooks_dir.glob('Import_*.ipynb'))

    if len(notebooks) == 0:
        print_error("Aucun notebook trouvé")
        return False

    print_success(f"{len(notebooks)} notebooks trouvés")

    for nb in sorted(notebooks)[:5]:  # Afficher les 5 premiers
        print_info(f"  • {nb.name}")

    if len(notebooks) > 5:
        print_info(f"  ... et {len(notebooks) - 5} autres")

    return True

def main():
    """Fonction principale"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{'PENNY ETL - VERIFICATION SYSTEME':^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

    checks = [
        ("Fichier .env", check_env_file),
        ("Variables d'environnement", check_env_variables),
        ("Docker", check_docker),
        ("PostgreSQL", check_postgresql_connection),
        ("Redshift", check_redshift_connection),
        ("Packages Python", check_python_packages),
        ("Notebooks", check_notebooks)
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Erreur lors de la vérification : {e}")
            results[name] = False

    # Résumé
    print_header("RÉSUMÉ")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, status in results.items():
        if status:
            print_success(name)
        else:
            print_error(name)

    print(f"\n{BLUE}{'='*70}{RESET}")

    if passed == total:
        print(f"\n{GREEN}[OK] Tous les tests sont passes ! ({passed}/{total}){RESET}")
        print(f"\n{GREEN}Vous pouvez lancer le scheduler : python src/notebook_scheduler.py{RESET}\n")
        return 0
    else:
        print(f"\n{YELLOW}[ATTENTION] {passed}/{total} tests passes{RESET}")
        print(f"\n{YELLOW}Corrigez les erreurs ci-dessus avant de lancer le scheduler.{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
