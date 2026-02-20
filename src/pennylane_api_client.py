"""
Client API REST Pennylane v2

Usage dans notebook:
    from src.pennylane_api_client import PennylaneClient

    client = PennylaneClient()
    df_customers = client.get_customers()
    df_invoices = client.get_customer_invoices()

Usage pour sync incrementale:
    client = PennylaneClient(env_path='.env')
    changes = client.get_changelog('customer_invoices', '2026-02-01T00:00:00Z')
    records = client.get_by_ids('/customer_invoices', [1, 2, 3])
"""

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from typing import Optional, Dict, List
from datetime import datetime


class PennylaneClient:
    """Client API REST Pennylane v2"""

    def __init__(self, env_path: str = None):
        if env_path:
            load_dotenv(dotenv_path=env_path)
        else:
            load_dotenv(dotenv_path='../../.env')

        self.api_token = os.getenv('PENNYLANE_API_TOKEN')
        self.api_base_url = os.getenv('PENNYLANE_API_BASE_URL', 'https://app.pennylane.com/api/external/v2')
        self.rate_limit = float(os.getenv('PENNYLANE_RATE_LIMIT', '4.5'))

        if not self.api_token:
            raise ValueError("PENNYLANE_API_TOKEN non trouve dans .env")

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

    # ========================================================================
    # METHODES HTTP DE BASE
    # ========================================================================

    def _wait_for_rate_limit(self):
        """Respecte le rate limit entre requetes"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None,
                      extra_headers: Optional[Dict] = None) -> Dict:
        """Requete GET avec rate limiting et retry 429"""
        url = f"{self.api_base_url}{endpoint}"
        headers = {**self.headers, **(extra_headers or {})}

        self._wait_for_rate_limit()

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"[WARNING] Rate limit atteint, attente {retry_after}s...")
                time.sleep(retry_after)
                return self._make_request(endpoint, params, extra_headers)
            elif response.status_code == 401:
                raise Exception("Token API invalide - Verifiez PENNYLANE_API_TOKEN dans .env")
            else:
                raise Exception(f"Erreur API {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            raise Exception("Timeout API - Verifiez votre connexion internet")

    def _make_post_request(self, endpoint: str, json_body: Optional[Dict] = None,
                           extra_headers: Optional[Dict] = None) -> Dict:
        """Requete POST avec rate limiting et retry 429"""
        url = f"{self.api_base_url}{endpoint}"
        headers = {**self.headers, **(extra_headers or {})}

        self._wait_for_rate_limit()

        try:
            response = requests.post(url, headers=headers, json=json_body, timeout=120)

            if response.status_code in (200, 201, 202):
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"[WARNING] Rate limit atteint, attente {retry_after}s...")
                time.sleep(retry_after)
                return self._make_post_request(endpoint, json_body, extra_headers)
            elif response.status_code == 401:
                raise Exception("Token API invalide - Verifiez PENNYLANE_API_TOKEN dans .env")
            else:
                raise Exception(f"Erreur API POST {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            raise Exception("Timeout API POST - Verifiez votre connexion internet")

    def _fetch_all_pages(self, endpoint: str, params: Optional[Dict] = None,
                         extra_headers: Optional[Dict] = None) -> List[Dict]:
        """Recupere toutes les pages d'un endpoint (pagination cursor-based API v2)"""
        all_data = []
        params = params or {}
        params['per_page'] = 100
        cursor = None
        page = 1

        print(f"[EXTRACT] Extraction {endpoint}...")

        while True:
            if cursor:
                params['cursor'] = cursor

            response = self._make_request(endpoint, params, extra_headers)

            if isinstance(response, dict) and 'items' in response:
                data = response['items']
                has_more = response.get('has_more', False)
                cursor = response.get('next_cursor')
            else:
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

        print(f"[OK] {len(all_data)} enregistrements recuperes\n")
        return all_data

    # ========================================================================
    # CHANGELOG & BATCH FETCH (sync incrementale)
    # ========================================================================

    def get_changelog(self, resource: str, start_date: str) -> List[Dict]:
        """
        Recupere le changelog d'une ressource depuis une date donnee.

        Args:
            resource: Nom de la ressource (customer_invoices, suppliers, etc.)
            start_date: Date ISO 8601 (ex: '2026-02-01T00:00:00Z')

        Returns:
            Liste des changements [{id, operation, timestamp}, ...]
        """
        all_changes = []
        params = {'start_date': start_date, 'per_page': 100}
        cursor = None
        page = 1

        print(f"[CHANGELOG] Lecture changelog {resource} depuis {start_date}...")

        while True:
            if cursor:
                params['cursor'] = cursor

            response = self._make_request(f'/changelogs/{resource}', params)

            if isinstance(response, dict) and 'items' in response:
                changes = response['items']
                has_more = response.get('has_more', False)
                cursor = response.get('next_cursor')
            else:
                changes = response if isinstance(response, list) else []
                has_more = False
                cursor = None

            if not changes:
                break

            all_changes.extend(changes)
            page += 1

            if not has_more and not cursor:
                break

        print(f"[CHANGELOG] {len(all_changes)} changements trouves pour {resource}")
        return all_changes

    def get_by_ids(self, endpoint: str, ids: List[int], batch_size: int = 100,
                   extra_headers: Optional[Dict] = None) -> List[Dict]:
        """
        Recupere des enregistrements par batch via filtre ID.

        Args:
            endpoint: Endpoint API (ex: '/customers')
            ids: Liste d'IDs a recuperer
            batch_size: Taille des batchs (max 100)
            extra_headers: Headers supplementaires

        Returns:
            Liste des enregistrements complets
        """
        if not ids:
            return []

        all_records = []
        batches = [ids[i:i + batch_size] for i in range(0, len(ids), batch_size)]

        print(f"[BATCH] Recuperation {len(ids)} enregistrements en {len(batches)} batch(s)...")

        for i, batch_ids in enumerate(batches, 1):
            filter_param = [{"field": "id", "operator": "in", "value": batch_ids}]
            params = {
                'filter': str(filter_param).replace("'", '"'),
                'per_page': batch_size
            }
            records = self._fetch_all_pages(endpoint, params, extra_headers)
            all_records.extend(records)
            print(f"  Batch {i}/{len(batches)}: {len(records)} enregistrements")

        print(f"[BATCH] Total: {len(all_records)} enregistrements recuperes")
        return all_records

    # ========================================================================
    # ENDPOINTS EXISTANTS (API REST)
    # ========================================================================

    def get_customers(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """Recupere la liste des clients"""
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/customers', params)

        if not data:
            print("[INFO] Aucun client trouve")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_customer_invoices(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """Recupere la liste des factures clients"""
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/customer_invoices', params)

        if not data:
            print("[INFO] Aucune facture client trouvee")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_suppliers(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """Recupere la liste des fournisseurs"""
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/suppliers', params)

        if not data:
            print("[INFO] Aucun fournisseur trouve")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_supplier_invoices(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """Recupere la liste des factures fournisseurs"""
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/supplier_invoices', params)

        if not data:
            print("[INFO] Aucune facture fournisseur trouvee")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_transactions(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """Recupere la liste des transactions bancaires"""
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/transactions', params)

        if not data:
            print("[INFO] Aucune transaction trouvee")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_products(self, updated_since: Optional[datetime] = None) -> pd.DataFrame:
        """Recupere la liste des produits/services"""
        params = {}
        if updated_since:
            params['filter[updated_at]'] = f"gte:{updated_since.strftime('%Y-%m-%dT%H:%M:%S')}"

        data = self._fetch_all_pages('/products', params)

        if not data:
            print("[INFO] Aucun produit trouve")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    # ========================================================================
    # NOUVEAUX ENDPOINTS (anciennement Redshift)
    # ========================================================================

    def get_ledger_entries(self) -> pd.DataFrame:
        """Recupere les ecritures comptables (grand livre general) via API v2"""
        data = self._fetch_all_pages(
            '/ledger_entries',
            extra_headers={'X-Use-2026-API-Changes': 'true'}
        )

        if not data:
            print("[INFO] Aucune ecriture comptable trouvee")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_ledger_accounts(self) -> pd.DataFrame:
        """Recupere le plan comptable via API v2"""
        data = self._fetch_all_pages(
            '/ledger_accounts',
            extra_headers={'X-Use-2026-API-Changes': 'true'}
        )

        if not data:
            print("[INFO] Aucun compte comptable trouve")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_bank_accounts(self) -> pd.DataFrame:
        """Recupere les comptes bancaires via API v2"""
        data = self._fetch_all_pages('/bank_accounts')

        if not data:
            print("[INFO] Aucun compte bancaire trouve")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def get_fiscal_years(self) -> pd.DataFrame:
        """Recupere les exercices fiscaux via API v2"""
        data = self._fetch_all_pages(
            '/fiscal_years',
            extra_headers={'X-Use-2026-API-Changes': 'true'}
        )

        if not data:
            print("[INFO] Aucun exercice fiscal trouve")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        print(f"[INFO] DataFrame cree: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    # ========================================================================
    # EXPORTS (FEC, Grand Livre Analytique)
    # ========================================================================

    def export_fec(self, fiscal_year_id: Optional[int] = None) -> Dict:
        """
        Lance un export FEC. Retourne l'URL de telechargement.

        Workflow : POST pour lancer → polling statut → URL de telechargement
        """
        body = {}
        if fiscal_year_id:
            body['fiscal_year_id'] = fiscal_year_id

        print("[EXPORT] Lancement export FEC...")
        response = self._make_post_request('/exports/fec', body)
        return self._poll_export(response)

    def export_analytical_ledger(self, start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> Dict:
        """
        Lance un export Grand Livre Analytique. Retourne l'URL de telechargement.

        Workflow : POST pour lancer → polling statut → URL de telechargement
        """
        body = {}
        if start_date:
            body['start_date'] = start_date
        if end_date:
            body['end_date'] = end_date

        print("[EXPORT] Lancement export Grand Livre Analytique...")
        response = self._make_post_request('/exports/analytical_general_ledger', body)
        return self._poll_export(response)

    def _poll_export(self, initial_response: Dict, max_wait: int = 300) -> Dict:
        """
        Polling sur un export asynchrone jusqu'a completion.

        Args:
            initial_response: Reponse du POST initial (contient id/status/url)
            max_wait: Temps max d'attente en secondes

        Returns:
            Reponse finale avec URL de telechargement
        """
        export_id = initial_response.get('id')
        status = initial_response.get('status', '')
        download_url = initial_response.get('download_url') or initial_response.get('url')

        if download_url and status in ('completed', 'done', ''):
            print(f"[EXPORT] Export pret immediatement")
            return initial_response

        if not export_id:
            print(f"[EXPORT] Reponse directe (pas de polling)")
            return initial_response

        print(f"[EXPORT] Export {export_id} en cours, polling...")
        start = time.time()

        while time.time() - start < max_wait:
            time.sleep(5)
            try:
                response = self._make_request(f'/exports/{export_id}')
                status = response.get('status', '')
                download_url = response.get('download_url') or response.get('url')

                if status in ('completed', 'done') or download_url:
                    print(f"[EXPORT] Export {export_id} termine")
                    return response
                elif status in ('failed', 'error'):
                    raise Exception(f"Export {export_id} echoue: {response}")

                print(f"  Status: {status}...")
            except Exception as e:
                if 'echoue' in str(e):
                    raise
                print(f"  Polling erreur (retry): {e}")

        raise Exception(f"Export {export_id} timeout apres {max_wait}s")

    def download_export(self, url: str) -> pd.DataFrame:
        """Telecharge un fichier d'export et le charge en DataFrame"""
        print(f"[DOWNLOAD] Telechargement export...")
        self._wait_for_rate_limit()

        response = requests.get(url, headers=self.headers, timeout=120)
        if response.status_code != 200:
            raise Exception(f"Erreur telechargement: {response.status_code}")

        content_type = response.headers.get('Content-Type', '')

        if 'csv' in content_type or url.endswith('.csv'):
            import io
            df = pd.read_csv(io.StringIO(response.text), sep=';')
        else:
            df = pd.read_csv(pd.io.common.StringIO(response.text), sep='\t')

        print(f"[DOWNLOAD] {len(df)} lignes chargees")
        return df

    # ========================================================================
    # UTILITAIRES
    # ========================================================================

    def test_connection(self) -> bool:
        """Teste la connexion API et affiche les informations utilisateur"""
        try:
            print("[TEST] Test de connexion API...")
            response = self._make_request('/me')

            user = response.get('user', {})
            company = response.get('company', {})

            print(f"[OK] Connexion reussie")
            print(f"  Utilisateur: {user.get('first_name')} {user.get('last_name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Societe: {company.get('name')} ({company.get('reg_no')})")
            return True

        except Exception as e:
            print(f"[ERREUR] Echec connexion: {e}")
            return False

    def fetch_all_raw(self, endpoint: str, extra_headers: Optional[Dict] = None) -> List[Dict]:
        """Acces direct a _fetch_all_pages pour usage dans incremental_sync"""
        return self._fetch_all_pages(endpoint, extra_headers=extra_headers)


if __name__ == "__main__":
    print("=" * 70)
    print("TEST CLIENT API PENNYLANE")
    print("=" * 70)
    print()

    load_dotenv()

    client = PennylaneClient(env_path='.env')

    if client.test_connection():
        print()

        df = client.get_customers()
        if not df.empty:
            print(f"[INFO] Apercu des clients:")
            print(df.head())
