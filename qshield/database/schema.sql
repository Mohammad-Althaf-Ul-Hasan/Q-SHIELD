-- ============================================================
-- Q-SHIELD Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS quantum_db;
USE quantum_db;

-- ------------------------------------------------------------
-- Table: messages
-- Stores encrypted messages for the encrypt/decrypt flow
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ciphertext TEXT NOT NULL,
    authentication_tag VARCHAR(128) NOT NULL,
    nonce VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Table: key_events
-- Immutable audit trail for every key generation event
-- Used by the blockchain audit module (Phase 12)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS key_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL UNIQUE,
    event_type VARCHAR(50) NOT NULL,
    qber_percent DECIMAL(6,3),
    key_fingerprint VARCHAR(128),
    node_count INT DEFAULT 2,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- ------------------------------------------------------------
-- Table: key_lifecycle
-- Tracks active keys for lifecycle management
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS key_lifecycle (
    key_id VARCHAR(64) PRIMARY KEY,
    key_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    status ENUM('active', 'revoked', 'expired') DEFAULT 'active',
    session_id VARCHAR(128)
);