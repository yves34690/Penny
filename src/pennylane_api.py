"""
Module d'extraction de données depuis l'API Pennylane
Gère le rate limiting, la pagination et les erreurs
"""

import requests
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PennylaneAPI:
    """Client pour l'API Pennylane avec gestion du rate limiting"""

    def __init__(self, api_key: str, base_url: str, rate_limit: float = 4.5):
        """
        Initialise le client API

        Args:
            api_key: Clé API Pennylane
            base_url: URL de base de l'API
            rate_limit: Nombre de requêtes par seconde (défaut: 4.5 pour marge de sécurité)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.rate_limit = rate_limit
        self.min_interval = 1.0 / rate_limit  # Intervalle minimum entre requêtes
        self.last_request_time = 0

        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _wait_for_rate_limit(self):
        """Attend si nécessaire pour respecter le rate limit"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_interval:
            sleep_time = self.min_interval - time_since_last_request
            logger.debug(f"Rate limit: attente de {sleep_time:.3f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None,
                     max_retries: int = 3) -> Dict:
        """
        Effectue une requête HTTP avec gestion des erreurs et retry

        Args:
            endpoint: Endpoint de l'API (ex: /customer_invoices)
            params: Paramètres de la requête
            max_retries: Nombre maximum de tentatives

        Returns:
            Réponse JSON de l'API
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()

                logger.debug(f"GET {url} (tentative {attempt + 1}/{max_retries})")
                response = requests.get(url, headers=self.headers, params=params, timeout=30)

                # Gestion des codes HTTP
                if response.status_code == 200:
                    return response.json()

                elif response.status_code == 429:  # Rate limit dépassé
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limit dépassé, attente de {retry_after}s")
                    time.sleep(retry_after)
                    continue

                elif response.status_code == 401:
                    raise Exception("Authentification invalide - Vérifiez votre clé API")

                elif response.status_code == 404:
                    raise Exception(f"Endpoint non trouvé: {endpoint}")

                elif response.status_code >= 500:
                    logger.warning(f"Erreur serveur {response.status_code}, retry...")
                    time.sleep(2 ** attempt)  # Backoff exponentiel
                    continue

                else:
                    response.raise_for_status()

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout sur {url}, tentative {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur requête: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

        raise Exception(f"Échec après {max_retries} tentatives")

    def get_paginated_data(self, endpoint: str, params: Optional[Dict] = None,
                          max_pages: Optional[int] = None) -> List[Dict]:
        """
        Récupère toutes les données paginées d'un endpoint

        Args:
            endpoint: Endpoint de l'API
            params: Paramètres supplémentaires
            max_pages: Limite du nombre de pages (None = toutes)

        Returns:
            Liste de tous les enregistrements
        """
        all_data = []
        page = 1
        params = params or {}

        logger.info(f"Extraction depuis {endpoint}")

        while True:
            if max_pages and page > max_pages:
                logger.info(f"Limite de pages atteinte ({max_pages})")
                break

            params['page'] = page
            params.setdefault('per_page', 100)  # Max par page

            try:
                response = self._make_request(endpoint, params)

                # Structure de réponse Pennylane
                if isinstance(response, dict):
                    # Certains endpoints retournent {data: [...], pagination: {...}}
                    if 'data' in response:
                        data = response['data']
                    # D'autres retournent directement une liste
                    elif isinstance(response, list):
                        data = response
                    # Ou un objet unique
                    else:
                        data = [response]
                else:
                    data = response if isinstance(response, list) else [response]

                if not data:
                    logger.info(f"Aucune donnée à la page {page}, fin de pagination")
                    break

                all_data.extend(data)
                logger.info(f"Page {page}: {len(data)} enregistrements (total: {len(all_data)})")

                # Vérifier s'il y a d'autres pages
                if isinstance(response, dict) and 'pagination' in response:
                    pagination = response['pagination']
                    if page >= pagination.get('total_pages', page):
                        break
                elif len(data) < params['per_page']:
                    # Si moins de résultats que demandé = dernière page
                    break

                page += 1

            except Exception as e:
                logger.error(f"Erreur lors de l'extraction page {page}: {e}")
                raise

        logger.info(f"Extraction terminée: {len(all_data)} enregistrements au total")
        return all_data

    def get_incremental_data(self, endpoint: str, last_sync_date: Optional[datetime] = None,
                            date_field: str = 'updated_at') -> List[Dict]:
        """
        Récupère les données modifiées depuis la dernière synchronisation

        Args:
            endpoint: Endpoint de l'API
            last_sync_date: Date de la dernière synchro
            date_field: Champ de date pour le filtre

        Returns:
            Liste des enregistrements modifiés
        """
        params = {}

        if last_sync_date:
            # Format ISO 8601
            date_str = last_sync_date.strftime('%Y-%m-%dT%H:%M:%S')
            params[f'filter[{date_field}]'] = f'gte:{date_str}'
            logger.info(f"Extraction incrémentielle depuis {date_str}")
        else:
            logger.info("Première extraction complète")

        return self.get_paginated_data(endpoint, params)

    def test_connection(self) -> bool:
        """
        Test la connexion à l'API

        Returns:
            True si la connexion fonctionne
        """
        try:
            logger.info("Test de connexion à l'API Pennylane...")
            response = self._make_request('/companies')
            logger.info("✓ Connexion réussie")
            return True
        except Exception as e:
            logger.error(f"✗ Échec de connexion: {e}")
            return False

    def get_available_endpoints(self) -> List[str]:
        """
        Liste les endpoints disponibles (liste prédéfinie)

        Returns:
            Liste des endpoints principaux
        """
        return [
            '/customer_invoices',
            '/supplier_invoices',
            '/customers',
            '/suppliers',
            '/transactions',
            '/journal_entries',
            '/plan_items',  # Plan comptable
            '/categories',
            '/payment_methods',
            '/products',
            '/companies'
        ]
