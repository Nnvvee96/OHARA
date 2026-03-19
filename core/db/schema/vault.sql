-- OHARA Vault Schema
-- Database: ohara_vault.db
-- Purpose: Immutable raw source storage
-- Version: 1.0 | 2026-02-21
-- INVARIANT: No UPDATE on content fields. No DELETE. Ever.

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS raw_items (
  -- Identity (content-addressed)
  id                          TEXT PRIMARY KEY,
  -- SHA256(content_bytes), prefixed: 'raw_' || hex(sha256(content))

  -- Provenance
  origin_url                  TEXT NOT NULL,
  domain                      TEXT NOT NULL,
  ingested_at                 TEXT NOT NULL,
  epoch_id                    TEXT NOT NULL,
  ingestion_agent             TEXT NOT NULL,
  -- librarian_id or 'human'

  -- Content
  content_type                TEXT NOT NULL
    CHECK(content_type IN ('html','pdf','text','json','audio_transcript','markdown')),
  content_hash                TEXT NOT NULL UNIQUE,
  -- SHA256 of raw bytes — must match id derivation
  content_path                TEXT NOT NULL,
  -- e.g. 'vault/raw/2026/02/21/<content_hash>.bin'
  content_size_bytes          INTEGER NOT NULL,

  -- Source Metadata
  source_tier                 TEXT NOT NULL
    CHECK(source_tier IN ('primary','secondary','aggregator','social','internal')),
  editorial_independence_score REAL NOT NULL DEFAULT 0.5
    CHECK(editorial_independence_score BETWEEN 0.0 AND 1.0),
  known_dependency_ids        TEXT NOT NULL DEFAULT '[]',
  -- JSON array of raw_item ids this source depends on

  -- Status (only mutable fields)
  processing_status           TEXT NOT NULL DEFAULT 'pending'
    CHECK(processing_status IN ('pending','processing','processed','failed','archived')),
  processing_error            TEXT,

  created_at                  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- Immutability: block updates to content fields
CREATE TRIGGER IF NOT EXISTS raw_items_immutability
BEFORE UPDATE ON raw_items
BEGIN
  SELECT CASE
    WHEN NEW.id != OLD.id
      THEN RAISE(ABORT, 'raw_items: id is immutable')
    WHEN NEW.origin_url != OLD.origin_url
      THEN RAISE(ABORT, 'raw_items: origin_url is immutable')
    WHEN NEW.content_hash != OLD.content_hash
      THEN RAISE(ABORT, 'raw_items: content_hash is immutable')
    WHEN NEW.content_path != OLD.content_path
      THEN RAISE(ABORT, 'raw_items: content_path is immutable')
    WHEN NEW.epoch_id != OLD.epoch_id
      THEN RAISE(ABORT, 'raw_items: epoch_id is immutable')
    WHEN NEW.domain != OLD.domain
      THEN RAISE(ABORT, 'raw_items: domain is immutable')
  END;
END;

-- No DELETE permitted
CREATE TRIGGER IF NOT EXISTS raw_items_no_delete
BEFORE DELETE ON raw_items
BEGIN
  SELECT RAISE(ABORT, 'raw_items: deletion is forbidden. Use processing_status=archived.');
END;

CREATE INDEX IF NOT EXISTS idx_raw_items_epoch    ON raw_items(epoch_id);
CREATE INDEX IF NOT EXISTS idx_raw_items_domain   ON raw_items(domain);
CREATE INDEX IF NOT EXISTS idx_raw_items_status   ON raw_items(processing_status);
CREATE INDEX IF NOT EXISTS idx_raw_items_ingested ON raw_items(ingested_at);
