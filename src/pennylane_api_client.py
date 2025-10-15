"""
Client API REST Pennylane pour notebooks Jupyter
Remplace la connexion Redshift par des appels API REST

Usage dans notebook:
    from src.pennylane_api_client import PennylaneClient

    client = PennylaneClient()
    df_customers = client.get_customers()
    df_invoices = client.get_customer_invoices()
"""

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from typing import Optional, Dict, List
from datetime import datetime


class PennylaneClient:
    """Client API REST Pennylane simplifié pour notebooks Jupyter"""

    def __init__(self, env_path: str = None):
        """
        Initialise le client API

        Args:
            env_path: Chemin vers fichier .env (détecte automatiquement depuis notebooks)
        """
        # Charger .env (détection automatique depuis notebooks)
        if env_path:
            load_dotenv(dotenv_path=env_path)
        else:
            # Essayer depuis racine projet (2 niveaux au-dessus)
            load_dotenv(dotenv_path='../../.env')

        # Configuration API
        self.api_token = os.getenv('PENNYLANE_API_TOKEN')
        self.api_base_url = os.getenv('PENNYLANE_API_BASE_URL', 'https://app.pennylane.com/api/external/v2')
        self.rate_limit = float(os.getenv('PENNYLANE_RATE_LIMIT', '4.5'))

        if not self.api_token:
            raise ValueError("PENNYLANE_API_TOKEN non trouvé dans .env")

        self.min_interval = 1.0 / self.rate_limit
        self.last_request_time = 0

        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        print(f"[OK] Client API initialise")
        print(f"  Base URL: {self.api_base_url}")
        print(f"  Rate limit: {self.rate_limit} req/sec")

    def _wait_for_rate_limit(self):
        """Respecte le rate limit entre requêtes"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Effectue une requête API avec rate limiting

        Args:
            endpoint: Endpoint API (ex: /customers)
            params: Paramètres query string

        Returns:
            Réponse JSON
        """
        url = f"{self.api_base_url}{endpoint}"

        self._wait_for_rate_limit()

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"[WARNING] Rate limit atteint, attente {retry_after}s...")
                time.sleep(retry_after)
                return self._make_request(endpoint, params)
            elif response.status_code == 401:
                raise Exception("Token API invalide - Vérifiez PENNYLANE_API_TOKEN dans .env")
            else:
                raise Exception(f"Erreur API {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            raise Exception("Timeout API - Vérifiez votre connexion internet")
        except Exception as e:
            raise Exception(f"Erreur requête API: {e}")

    def _fetch_all_pages(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Récupère toutes les pages d'un endpoint (pagination cursor-based API v2)

        Args:
            endpoint: Endpoint API
            params: Paramètres supplémentaires

        Returns:
            Liste de tous les enregistrements
        """
        all_data = []
        params = params or {}
        params['per_page'] = 100
        cursor = None
        page = 1

        print(f"[EXTRACT] Extraction {endpoint}...")

        while True:
            if cursor:
                params['cursor'] = cursor

            response = self._make_request(endpoint, params)

            # API v2 utilise 'items' + cursor pagination
            if isinstance(response, dict) and 'items' in response:
                data = response['items']
                has_more = response.get('has_more', False)
                cursor = response.get('next_cursor')
            else:
                # Fallback pour autres formats
                data = response if isinstance(response, list) else []
                has_more = False
                cursor = None

            if not data:
                break

            all_data.extend(data)
            print(f"  Page {page}: {len(data)} enregistrements (total: {len(all_data)})")

            if not has_more and not cursor:
                break

            page += 1

        print(f"[OK] {len(all_data)} enregistrements récupérés\n")
        return all_data

    # ========================================================================
    # MÉTHODES PRATIQUES POUR CHAQUE ENDPOINT
    # ========================================================================

    def get_customers(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """
        Récupère la liste des clients

        Args:
            updated_since: Filtre sur updated_at >= date

        Returns:
            DataFrame pandas avec les clients
        """
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/customers', params)

        if not data:
            print("[INFO] Aucun client trouvé")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame créé: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_customer_invoices(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """
        Récupère la liste des factures clients

        Args:
            updated_since: Filtre sur updated_at >= date

        Returns:
            DataFrame pandas avec les factures
        """
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/customer_invoices', params)

        if not data:
            print("[INFO] Aucune facture client trouvée")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame créé: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_suppliers(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """
        Récupère la liste des fournisseurs

        Args:
            updated_since: Filtre sur updated_at >= date

        Returns:
            DataFrame pandas avec les fournisseurs
        """
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/suppliers', params)

        if not data:
            print("[INFO] Aucun fournisseur trouvé")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame créé: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_supplier_invoices(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """
        Récupère la liste des factures fournisseurs

        Args:
            updated_since: Filtre sur updated_at >= date

        Returns:
            DataFrame pandas avec les factures
        """
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/supplier_invoices', params)

        if not data:
            print("[INFO] Aucune facture fournisseur trouvée")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame créé: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_transactions(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """
        Récupère la liste des transactions bancaires

        Args:
            updated_since: Filtre sur updated_at >= date

        Returns:
            DataFrame pandas avec les transactions
        """
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/transactions', params)

        if not data:
            print("[INFO] Aucune transaction trouvée")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame créé: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_products(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """
        Récupère la liste des produits/services

        Args:
            updated_since: Filtre sur updated_at >= date

        Returns:
            DataFrame pandas avec les produits
        """
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/products', params)

        if not data:
            print("[INFO] Aucun produit trouvé")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame créé: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def test_connection(self) -> bool:
        """
        Teste la connexion API et affiche les informations utilisateur

        Returns:
            True si connexion OK
        """
        try:
            print("[TEST] Test de connexion API...")
            response = self._make_request('/me')

            user = response.get('user', {})
            company = response.get('company', {})

            print(f"[OK] Connexion réussie")
            print(f"  Utilisateur: {user.get('first_name')} {user.get('last_name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Société: {company.get('name')} ({company.get('reg_no')})")
            return True

        except Exception as e:
            print(f"[ERREUR] Échec connexion: {e}")
            return False


# ============================================================================
# EXEMPLE D'UTILISATION DANS NOTEBOOK
# ============================================================================

def exemple_utilisation():
    """
    Exemple d'utilisation dans un notebook Jupyter

    Copier-coller ces cellules dans votre notebook:
    """

    # Cellule 1: Import et initialisation
    code_cellule_1 = """
# Import client API
from src.pennylane_api_client import PennylaneClient

# Initialiser client
client = PennylaneClient()

# Tester connexion
client.test_connection()
"""

    # Cellule 2: Récupérer customers
    code_cellule_2 = """
# Récupérer tous les clients
df_customers = client.get_customers()

# Afficher aperçu
print(f"Colonnes disponibles: {list(df_customers.columns)}")
df_customers.head()
"""

    # Cellule 3: Récupérer invoices avec filtre date
    code_cellule_3 = """
from datetime import datetime, timedelta

# Factures modifiées dans les 7 derniers jours
date_7j = datetime.now() - timedelta(days=7)
df_invoices = client.get_customer_invoices(updated_since=date_7j)

# Afficher
df_invoices.head()
"""

    # Cellule 4: Export PostgreSQL
    code_cellule_4 = """
from sqlalchemy import create_engine
import os

# Connexion PostgreSQL
engine = create_engine(
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

# Export vers PostgreSQL
df_customers.to_sql(
    name='customers',
    con=engine,
    schema='pennylane',
    if_exists='replace',
    index=False
)

print(f"[OK] {len(df_customers)} clients exportés vers PostgreSQL")
"""

    return {
        '1_init': code_cellule_1,
        '2_customers': code_cellule_2,
        '3_invoices_filtered': code_cellule_3,
        '4_export_postgres': code_cellule_4
    }


if __name__ == "__main__":
    # Test du client en ligne de commande
    print("="*70)
    print("TEST CLIENT API PENNYLANE")
    print("="*70)
    print()

    # Charger .env depuis racine projet
    load_dotenv()

    # Initialiser client
    client = PennylaneClient(env_path='.env')

    # Tester connexion
    if client.test_connection():
        print()

        # Tester extraction customers
        df = client.get_customers()
        if not df.empty:
            print(f"[INFO] Aperçu des clients:")
            print(df.head())
