-- OHARA Knowledge Schema
-- Database: ohara_knowledge.db
-- Purpose: Atoms, Patterns, CounterEvidence, Books
-- Version: 1.0 | 2026-02-21

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;

-- ============================================================
-- ATOMS
-- ============================================================

CREATE TABLE IF NOT EXISTS atoms (
  -- Identity (content-addressed)
  id                        TEXT PRIMARY KEY,
  -- SHA256(claim_normalized || source_hash_set || epoch_id)
  -- Format: 'atom_' || hex(sha256(...))

  -- Core Claim
  claim                     TEXT NOT NULL,
  claim_type                TEXT NOT NULL
    CHECK(claim_type IN (
      'trend','tactic','structural_shift','failure_mode',
      'metric','principle','speculation','observation'
    )),

  -- Domain
  domain                    TEXT NOT NULL,
  cross_domain_tags         TEXT NOT NULL DEFAULT '[]',
  -- JSON array of additional domain strings

  -- Utility Vector (SOUL.md — Nutzbreite)
  utility_vector            TEXT NOT NULL DEFAULT '[]',
  -- JSON array of potential utility types. An atom can have multiple.
  -- Valid values:
  --   "product_building"      → could lead to building a product, app, SaaS, tool
  --   "process_improvement"   → improves or automates an existing process
  --   "system_enhancement"    → enhances/extends/replaces a system component
  --   "financial"             → directly applicable to trading, investing, revenue
  --   "future_optionality"    → no clear use now, but worth preserving for future context
  --   "personal_capability"   → improves a person's skill, judgment, or knowledge
  --   "creative_enabling"     → enables new forms of creation (content, design, media)
  --   "decision_support"      → helps make better decisions with less uncertainty
  --   "self_improvement"      → improves the Wissenden themselves — their methods, evaluation logic, domain understanding
  -- An atom with empty utility_vector after validation = candidate for rejection.
  -- Rationale: OHARA is not an archive. If it has no potential utility in any form,
  -- it does not belong in the library. (See SOUL.md)

  -- Provenance (INVARIANT-2: all mandatory)
  source_ids                TEXT NOT NULL,
  -- JSON array of raw_item ids
  source_hash_set           TEXT NOT NULL,
  -- SHA256(JSON.stringify(sorted source_ids))
  epoch_id                  TEXT NOT NULL,
  model_id                  TEXT NOT NULL,
  extraction_parameters     TEXT NOT NULL,
  -- JSON: { prompt_version, temperature, max_tokens }
  extracted_by              TEXT NOT NULL,
  -- librarian_id or 'human'
  extracted_at              TEXT NOT NULL,

  -- Epistemic Scores
  speculation_level         INTEGER NOT NULL
    CHECK(speculation_level BETWEEN 1 AND 5),
  confidence_score          REAL NOT NULL
    CHECK(confidence_score BETWEEN 0.0 AND 1.0),
  source_independence_score REAL,
  -- NULL until validation pass
  convergence_count         INTEGER NOT NULL DEFAULT 1,
  temporal_first_seen       TEXT,
  temporal_last_seen        TEXT,

  -- Lifecycle
  status                    TEXT NOT NULL DEFAULT 'candidate'
    CHECK(status IN ('candidate','accepted','rejected','superseded')),
  superseded_by             TEXT REFERENCES atoms(id),
  rejection_reason          TEXT,

  created_at                TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),

  -- Constraints
  CONSTRAINT claim_length CHECK(length(claim) <= 280),
  CONSTRAINT source_ids_not_empty CHECK(json_array_length(source_ids) >= 1),
  CONSTRAINT superseded_requires_pointer CHECK(
    status != 'superseded' OR superseded_by IS NOT NULL
  ),
  CONSTRAINT rejected_requires_reason CHECK(
    status != 'rejected' OR rejection_reason IS NOT NULL
  )
);

CREATE TRIGGER IF NOT EXISTS atoms_no_delete
BEFORE DELETE ON atoms
BEGIN
  SELECT RAISE(ABORT, 'atoms: deletion forbidden. Use status=superseded with superseded_by.');
END;

CREATE INDEX IF NOT EXISTS idx_atoms_domain     ON atoms(domain);
CREATE INDEX IF NOT EXISTS idx_atoms_status     ON atoms(status);
CREATE INDEX IF NOT EXISTS idx_atoms_claim_type ON atoms(claim_type);
CREATE INDEX IF NOT EXISTS idx_atoms_epoch      ON atoms(epoch_id);

-- ============================================================
-- PATTERNS
-- ============================================================

CREATE TABLE IF NOT EXISTS patterns (
  -- Identity (stable, not content-addressed — patterns evolve)
  id                          TEXT PRIMARY KEY,
  -- Format: 'pat_' || ulid()

  -- Definition
  title                       TEXT NOT NULL,
  summary                     TEXT NOT NULL,
  domain                      TEXT NOT NULL,
  cross_domain_tags           TEXT NOT NULL DEFAULT '[]',

  -- Lifecycle
  status                      TEXT NOT NULL DEFAULT 'signal'
    CHECK(status IN ('signal','emerging','validated','structural','deprecated')),
  status_changed_at           TEXT NOT NULL,

  -- Constituent Atoms
  atom_ids                    TEXT NOT NULL DEFAULT '[]',
  -- JSON array — append only
  atom_count                  INTEGER NOT NULL DEFAULT 0,

  -- Provenance (INVARIANT-2)
  source_hash_set             TEXT NOT NULL,
  epoch_id                    TEXT NOT NULL,
  version                     INTEGER NOT NULL DEFAULT 1,

  -- Epistemic Scores
  confidence_score_avg        REAL,
  source_independence_score   REAL,
  cross_domain_count          INTEGER NOT NULL DEFAULT 0,
  temporal_span_days          INTEGER,

  -- Counter-Evidence Summary (denormalized)
  counter_evidence_count      INTEGER NOT NULL DEFAULT 0,
  unresolved_strong_count     INTEGER NOT NULL DEFAULT 0,
  -- > 0 BLOCKS all promotion — hard constraint

  -- Human Sign-off (VALIDATED → STRUCTURAL only)
  structural_approved_by      TEXT,
  structural_approved_at      TEXT,
  structural_rationale        TEXT,

  -- Deprecation
  deprecated_reason           TEXT,
  superseded_by_pattern_id    TEXT REFERENCES patterns(id),

  created_at                  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  updated_at                  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  created_by                  TEXT NOT NULL,
  updated_by                  TEXT NOT NULL,

  CONSTRAINT title_length CHECK(length(title) <= 120),
  CONSTRAINT summary_length CHECK(length(summary) <= 500),
  CONSTRAINT structural_requires_human CHECK(
    status != 'structural' OR (
      structural_approved_by IS NOT NULL AND
      structural_approved_at IS NOT NULL AND
      structural_rationale IS NOT NULL AND
      length(structural_rationale) >= 100
    )
  ),
  CONSTRAINT deprecation_requires_reason CHECK(
    status != 'deprecated' OR deprecated_reason IS NOT NULL
  )
);

-- Append-only audit log for every status change
CREATE TABLE IF NOT EXISTS pattern_history (
  id                    TEXT PRIMARY KEY,
  pattern_id            TEXT NOT NULL REFERENCES patterns(id),
  version               INTEGER NOT NULL,
  status_from           TEXT NOT NULL,
  status_to             TEXT NOT NULL,
  changed_at            TEXT NOT NULL,
  changed_by            TEXT NOT NULL,
  epoch_id              TEXT NOT NULL,
  promotion_evidence    TEXT,
  -- JSON: scores at time of promotion
  skeptic_cycle_id      TEXT,
  -- Required for EMERGING → VALIDATED
  rationale             TEXT NOT NULL,

  UNIQUE(pattern_id, version)
);

CREATE TRIGGER IF NOT EXISTS patterns_no_delete
BEFORE DELETE ON patterns
BEGIN
  SELECT RAISE(ABORT, 'patterns: deletion forbidden. Use status=deprecated.');
END;

CREATE INDEX IF NOT EXISTS idx_patterns_domain        ON patterns(domain);
CREATE INDEX IF NOT EXISTS idx_patterns_status        ON patterns(status);
CREATE INDEX IF NOT EXISTS idx_pattern_history_pat    ON pattern_history(pattern_id);

-- ============================================================
-- COUNTER EVIDENCE
-- ============================================================

CREATE TABLE IF NOT EXISTS counter_evidence (
  id                      TEXT PRIMARY KEY,
  -- Format: 'ce_' || ulid()

  -- Relational links
  atom_id                 TEXT NOT NULL REFERENCES atoms(id),
  contradicts_pattern_id  TEXT NOT NULL REFERENCES patterns(id),

  -- Classification
  severity                TEXT NOT NULL
    CHECK(severity IN ('weak','moderate','strong','fatal')),

  -- Resolution
  resolution_status       TEXT NOT NULL DEFAULT 'unresolved'
    CHECK(resolution_status IN (
      'unresolved','under_review','acknowledged','refuted','integrated'
    )),
  resolution_rationale    TEXT,
  resolved_by             TEXT,
  resolved_at             TEXT,

  -- Provenance
  epoch_id                TEXT NOT NULL,
  proposed_by             TEXT NOT NULL,
  proposed_at             TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),

  CONSTRAINT refuted_requires_rationale CHECK(
    resolution_status != 'refuted' OR resolution_rationale IS NOT NULL
  ),
  CONSTRAINT integrated_requires_rationale CHECK(
    resolution_status != 'integrated' OR resolution_rationale IS NOT NULL
  ),
  CONSTRAINT resolved_requires_resolver CHECK(
    resolution_status IN ('unresolved','under_review') OR resolved_by IS NOT NULL
  )
);

-- Update pattern counter_evidence counts on insert
CREATE TRIGGER IF NOT EXISTS ce_update_on_insert
AFTER INSERT ON counter_evidence
BEGIN
  UPDATE patterns
  SET
    counter_evidence_count = (
      SELECT COUNT(*) FROM counter_evidence
      WHERE contradicts_pattern_id = NEW.contradicts_pattern_id
    ),
    unresolved_strong_count = (
      SELECT COUNT(*) FROM counter_evidence
      WHERE contradicts_pattern_id = NEW.contradicts_pattern_id
        AND severity IN ('strong','fatal')
        AND resolution_status = 'unresolved'
    )
  WHERE id = NEW.contradicts_pattern_id;
END;

-- Update pattern unresolved_strong_count on resolution
CREATE TRIGGER IF NOT EXISTS ce_update_on_resolution
AFTER UPDATE OF resolution_status ON counter_evidence
BEGIN
  UPDATE patterns
  SET unresolved_strong_count = (
    SELECT COUNT(*) FROM counter_evidence
    WHERE contradicts_pattern_id = NEW.contradicts_pattern_id
      AND severity IN ('strong','fatal')
      AND resolution_status = 'unresolved'
  )
  WHERE id = NEW.contradicts_pattern_id;
END;

CREATE INDEX IF NOT EXISTS idx_ce_pattern  ON counter_evidence(contradicts_pattern_id);
CREATE INDEX IF NOT EXISTS idx_ce_status   ON counter_evidence(resolution_status);
CREATE INDEX IF NOT EXISTS idx_ce_severity ON counter_evidence(severity);

-- ============================================================
-- SKEPTIC CYCLES
-- ============================================================

CREATE TABLE IF NOT EXISTS skeptic_cycles (
  id                          TEXT PRIMARY KEY,
  -- Format: 'skep_' || ulid()

  pattern_id                  TEXT NOT NULL REFERENCES patterns(id),
  epoch_id                    TEXT NOT NULL,
  triggered_by                TEXT NOT NULL,
  -- 'system' (pre-promotion gate) or 'human' (manual audit)
  trigger_reason              TEXT NOT NULL
    CHECK(trigger_reason IN ('pre_promotion','monthly_audit','manual')),

  started_at                  TEXT NOT NULL,
  completed_at                TEXT,
  sources_searched            INTEGER NOT NULL DEFAULT 0,
  counter_evidence_proposed   INTEGER NOT NULL DEFAULT 0,

  status                      TEXT NOT NULL DEFAULT 'pending'
    CHECK(status IN ('pending','completed','failed')),
  failure_reason              TEXT,
  notes                       TEXT,

  created_at                  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_skep_pattern ON skeptic_cycles(pattern_id);
CREATE INDEX IF NOT EXISTS idx_skep_status  ON skeptic_cycles(status);

-- ============================================================
-- BOOKS
-- ============================================================

CREATE TABLE IF NOT EXISTS books (
  id                      TEXT PRIMARY KEY,
  -- Format: 'book_' || ulid()

  title                   TEXT NOT NULL,
  domain                  TEXT NOT NULL,
  description             TEXT NOT NULL,

  status                  TEXT NOT NULL DEFAULT 'draft'
    CHECK(status IN ('draft','active','archived')),
  version                 INTEGER NOT NULL DEFAULT 1,

  -- Provenance (INVARIANT-2)
  epoch_id                TEXT NOT NULL,
  source_hash_set         TEXT NOT NULL,

  -- Content
  open_questions          TEXT NOT NULL DEFAULT '[]',
  -- JSON array of unresolved questions preserved for future investigation
  change_log              TEXT NOT NULL DEFAULT '[]',
  -- JSON array of { version, changed_at, changed_by, summary }

  -- Staleness
  stale_dependency_count  INTEGER NOT NULL DEFAULT 0,

  created_at              TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  updated_at              TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  created_by              TEXT NOT NULL,
  updated_by              TEXT NOT NULL
);

-- ============================================================
-- BOOK PATTERN DEPENDENCIES
-- ============================================================

CREATE TABLE IF NOT EXISTS book_pattern_dependencies (
  id                              TEXT PRIMARY KEY,
  book_id                         TEXT NOT NULL REFERENCES books(id),
  pattern_id                      TEXT NOT NULL REFERENCES patterns(id),

  pattern_version_snapshot        INTEGER NOT NULL,
  pattern_status_at_inclusion     TEXT NOT NULL,
  pattern_confidence_at_inclusion REAL NOT NULL,

  staleness_status                TEXT NOT NULL DEFAULT 'current'
    CHECK(staleness_status IN ('current','stale','deprecated_dependency')),

  cascade_policy                  TEXT NOT NULL DEFAULT 'manual_review'
    CHECK(cascade_policy IN ('auto_flag','block_book_update','manual_review')),

  included_at                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  included_by                     TEXT NOT NULL,

  UNIQUE(book_id, pattern_id)
);

-- Flag stale book dependencies when pattern is updated
CREATE TRIGGER IF NOT EXISTS bpd_staleness_on_pattern_update
AFTER UPDATE ON patterns
BEGIN
  UPDATE book_pattern_dependencies
  SET staleness_status = CASE
    WHEN NEW.status = 'deprecated' THEN 'deprecated_dependency'
    WHEN NEW.version != pattern_version_snapshot THEN 'stale'
    ELSE staleness_status
  END
  WHERE pattern_id = NEW.id
    AND staleness_status = 'current';

  UPDATE books
  SET stale_dependency_count = (
    SELECT COUNT(*) FROM book_pattern_dependencies
    WHERE book_id = books.id
      AND staleness_status != 'current'
  )
  WHERE id IN (
    SELECT book_id FROM book_pattern_dependencies WHERE pattern_id = NEW.id
  );
END;

CREATE INDEX IF NOT EXISTS idx_bpd_book       ON book_pattern_dependencies(book_id);
CREATE INDEX IF NOT EXISTS idx_bpd_pattern    ON book_pattern_dependencies(pattern_id);
CREATE INDEX IF NOT EXISTS idx_bpd_staleness  ON book_pattern_dependencies(staleness_status);

-- ============================================================
-- CROSS-DOMAIN COLLABORATION LOG
-- ============================================================
-- Tracks when a wizard references another domain's atom/pattern
-- Foundation for future collaboration protocol

CREATE TABLE IF NOT EXISTS cross_domain_references (
  id              TEXT PRIMARY KEY,
  source_domain   TEXT NOT NULL,
  target_domain   TEXT NOT NULL,
  source_atom_id  TEXT REFERENCES atoms(id),
  target_atom_id  TEXT REFERENCES atoms(id),
  pattern_id      TEXT REFERENCES patterns(id),
  reference_type  TEXT NOT NULL
    CHECK(reference_type IN ('atom_shared','pattern_referenced','book_cited')),
  noted_by        TEXT NOT NULL,
  noted_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_xref_source ON cross_domain_references(source_domain);
CREATE INDEX IF NOT EXISTS idx_xref_target ON cross_domain_references(target_domain);
