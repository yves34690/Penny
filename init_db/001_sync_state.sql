-- ============================================================================
-- Table de suivi des synchronisations incrementales Pennylane
-- Executee automatiquement au demarrage de incremental_sync.py
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS pennylane;

CREATE TABLE IF NOT EXISTS pennylane.sync_state (
    table_name VARCHAR(100) PRIMARY KEY,
    last_sync_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_processed_at VARCHAR(255),
    records_synced INTEGER DEFAULT 0,
    sync_type VARCHAR(20) DEFAULT 'full',
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE pennylane.sync_state IS 'Etat des synchronisations incrementales Pennylane -> PostgreSQL';
COMMENT ON COLUMN pennylane.sync_state.table_name IS 'Nom de la table synchronisee (ex: customers, customer_invoices)';
COMMENT ON COLUMN pennylane.sync_state.last_sync_at IS 'Date de derniere synchronisation reussie';
COMMENT ON COLUMN pennylane.sync_state.last_processed_at IS 'Dernier cursor/timestamp traite (pour reprise)';
COMMENT ON COLUMN pennylane.sync_state.records_synced IS 'Nombre enregistrements synchronises lors derniere sync';
COMMENT ON COLUMN pennylane.sync_state.sync_type IS 'Type de derniere sync: full ou incremental';
