"""
Module de transformations de données
Transformations basiques - Transformations spécifiques à faire dans Jupyter Notebook
"""

import pandas as pd
import logging
from typing import Dict
import re

logger = logging.getLogger(__name__)


class DataTransformer:
    """Applique uniquement des transformations basiques - Le reste dans Jupyter"""

    def __init__(self, config: Dict):
        """
        Initialise le transformateur

        Args:
            config: Configuration depuis config.json
        """
        self.config = config

    def basic_transform(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Applique uniquement les transformations basiques avant stockage brut

        Args:
            df: DataFrame à transformer
            table_name: Nom de la table

        Returns:
            DataFrame avec transformations minimales
        """
        if df.empty:
            logger.warning(f"DataFrame vide pour {table_name}")
            return df

        logger.info(f"Nettoyage basique de {table_name} ({len(df)} lignes)")

        # Normaliser noms de colonnes
        df = self.normalize_column_names(df)

        # Nettoyage minimal
        df = df.drop_duplicates()

        logger.info(f"Nettoyage terminé: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    @staticmethod
    def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalise les noms de colonnes (snake_case, sans caractères spéciaux)

        Args:
            df: DataFrame à normaliser

        Returns:
            DataFrame avec colonnes normalisées
        """
        def normalize_name(name: str) -> str:
            # Minuscules
            name = name.lower()
            # Remplacer espaces et tirets par underscore
            name = re.sub(r'[\s\-]+', '_', name)
            # Supprimer caractères spéciaux
            name = re.sub(r'[^\w_]', '', name)
            # Supprimer underscores multiples
            name = re.sub(r'_+', '_', name)
            # Supprimer underscores en début/fin
            name = name.strip('_')
            return name

        df.columns = [normalize_name(col) for col in df.columns]
        return df

    @staticmethod
    def flatten_nested_json(df: pd.DataFrame, max_depth: int = 2) -> pd.DataFrame:
        """
        Aplatit les structures JSON imbriquées en colonnes distinctes

        Args:
            df: DataFrame contenant des colonnes JSON
            max_depth: Profondeur maximale d'aplatissement

        Returns:
            DataFrame avec colonnes aplaties
        """
        def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict) and parent_key.count(sep) < max_depth:
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    items.append((new_key, str(v)))
                else:
                    items.append((new_key, v))
            return dict(items)

        # Identifier colonnes avec objets dict
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, dict)).any():
                logger.debug(f"Aplatissement de la colonne {col}")
                flattened = df[col].apply(lambda x: flatten_dict(x) if isinstance(x, dict) else {})
                flattened_df = pd.json_normalize(flattened)

                # Préfixer avec nom colonne d'origine
                flattened_df.columns = [f"{col}_{subcol}" for subcol in flattened_df.columns]

                # Fusionner avec df original
                df = df.drop(columns=[col])
                df = pd.concat([df, flattened_df], axis=1)

        return df

    @staticmethod
    def add_date_dimensions(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """
        Ajoute des colonnes de dimension temporelle (année, mois, trimestre, etc.)

        Args:
            df: DataFrame
            date_col: Nom de la colonne date

        Returns:
            DataFrame avec dimensions temporelles
        """
        if date_col not in df.columns:
            logger.warning(f"Colonne {date_col} introuvable pour dimensions temporelles")
            return df

        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

            df[f'{date_col}_annee'] = df[date_col].dt.year
            df[f'{date_col}_mois'] = df[date_col].dt.month
            df[f'{date_col}_trimestre'] = df[date_col].dt.quarter
            df[f'{date_col}_semaine'] = df[date_col].dt.isocalendar().week
            df[f'{date_col}_jour_semaine'] = df[date_col].dt.dayofweek
            df[f'{date_col}_nom_mois'] = df[date_col].dt.month_name()

            logger.debug(f"Dimensions temporelles ajoutées pour {date_col}")

        except Exception as e:
            logger.warning(f"Erreur lors de l'ajout des dimensions temporelles: {e}")

        return df
