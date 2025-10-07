-- Script d'initialisation de la base de données Pennylane
-- Créé automatiquement au premier démarrage de PostgreSQL

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Schema dédié pour les données Pennylane
CREATE SCHEMA IF NOT EXISTS pennylane;

-- Table de logs des actualisations
CREATE TABLE IF NOT EXISTS pennylane.etl_logs (
    id SERIAL PRIMARY KEY,
    execution_date TIMESTAMP DEFAULT NOW(),
    table_name VARCHAR(255),
    records_extracted INTEGER,
    records_loaded INTEGER,
    status VARCHAR(50),
    error_message TEXT,
    execution_time_seconds NUMERIC(10, 2)
);

-- Index pour requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_etl_logs_date ON pennylane.etl_logs(execution_date DESC);
CREATE INDEX IF NOT EXISTS idx_etl_logs_table ON pennylane.etl_logs(table_name);

-- Table pour stocker les métadonnées des dernières synchros
CREATE TABLE IF NOT EXISTS pennylane.sync_metadata (
    table_name VARCHAR(255) PRIMARY KEY,
    last_sync_date TIMESTAMP,
    last_record_id VARCHAR(255),
    total_records INTEGER
);

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA pennylane TO pennylane_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA pennylane TO pennylane_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA pennylane TO pennylane_user;

-- Configuration pour Power BI
ALTER DEFAULT PRIVILEGES IN SCHEMA pennylane GRANT SELECT ON TABLES TO pennylane_user;

COMMENT ON SCHEMA pennylane IS 'Schéma contenant les données synchronisées depuis l''API Pennylane';
COMMENT ON TABLE pennylane.etl_logs IS 'Historique des exécutions ETL';
COMMENT ON TABLE pennylane.sync_metadata IS 'Métadonnées des synchronisations pour actualisation incrémentielle';
