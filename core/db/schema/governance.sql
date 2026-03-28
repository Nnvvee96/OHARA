-- OHARA Governance Schema
-- Database: ohara_governance.db
-- Purpose: Epochs, Prompt Registry, Vitality Signals, Governance Actions, Wizard Registry
-- Version: 1.0 | 2026-02-21

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;

-- ============================================================
-- WIZARD REGISTRY
-- ============================================================

CREATE TABLE IF NOT EXISTS wizards (
  id              TEXT PRIMARY KEY,
  -- Format: 'wiz_' || short_name  e.g. 'wiz_aria'

  -- Identity
  name            TEXT NOT NULL UNIQUE,
  -- Full name e.g. 'Aria Chen'
  short_name      TEXT NOT NULL UNIQUE,
  -- e.g. 'aria' — used in IDs and CLI
  domain          TEXT NOT NULL,
  specialty       TEXT NOT NULL,
  -- One-line description of their specific niche

  -- Persona (shapes LLM prompts)
  persona_summary TEXT NOT NULL,
  -- 2-3 sentences describing personality, evaluation style, biases
  persona_full    TEXT NOT NULL,
  -- Full persona prompt injected into every LLM call

  -- Signal Perimeter
  signal_sources  TEXT NOT NULL DEFAULT '[]',
  -- JSON array of source configs: { type, url_or_query, priority }

  -- Status
  status          TEXT NOT NULL DEFAULT 'active'
    CHECK(status IN ('active','inactive','suspended','retired')),
  activation_date TEXT NOT NULL,
  suspended_reason TEXT,

  -- Collaboration
  known_collaborators TEXT NOT NULL DEFAULT '[]',
  -- JSON array of wizard short_names this wizard cross-references
  -- Grows organically as collaboration is detected

  created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_wizards_domain ON wizards(domain);
CREATE INDEX IF NOT EXISTS idx_wizards_status ON wizards(status);

-- ============================================================
-- EPOCHS
-- ============================================================

CREATE TABLE IF NOT EXISTS epochs (
  id              TEXT PRIMARY KEY,
  -- Format: 'epoch_' || YYYYMMDD || '_' || 4chars
  -- e.g. 'epoch_20260221_cal0'

  name            TEXT NOT NULL,
  description     TEXT NOT NULL,
  wizard_id       TEXT,
  -- NULL = global epoch. Set = wizard-scoped epoch.

  -- Frozen Parameters (INVARIANT-3)
  extraction_prompt_version TEXT NOT NULL,
  model_id        TEXT NOT NULL,
  model_version   TEXT NOT NULL,
  -- No 'latest' aliases. Pinned only.
  signal_sources  TEXT NOT NULL,
  -- JSON snapshot of source list at epoch creation
  scoring_thresholds TEXT NOT NULL,
  -- JSON: all numeric promotion thresholds
  anomaly_thresholds TEXT NOT NULL,
  -- JSON: all anomaly detection thresholds

  -- Lifecycle
  status          TEXT NOT NULL DEFAULT 'active'
    CHECK(status IN ('active','closed','superseded')),
  started_at      TEXT NOT NULL,
  closed_at       TEXT,
  superseded_by   TEXT REFERENCES epochs(id),
  closed_reason   TEXT,

  created_by      TEXT NOT NULL,
  created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),

  CONSTRAINT closed_requires_reason CHECK(
    status = 'active' OR closed_reason IS NOT NULL
  )
);

-- Freeze parameters when epoch is active
CREATE TRIGGER IF NOT EXISTS epochs_freeze_on_active
BEFORE UPDATE ON epochs
WHEN OLD.status = 'active'
BEGIN
  SELECT CASE
    WHEN NEW.extraction_prompt_version != OLD.extraction_prompt_version
      THEN RAISE(ABORT, 'epochs: extraction_prompt_version is frozen in active epoch')
    WHEN NEW.model_id != OLD.model_id
      THEN RAISE(ABORT, 'epochs: model_id is frozen in active epoch')
    WHEN NEW.model_version != OLD.model_version
      THEN RAISE(ABORT, 'epochs: model_version is frozen in active epoch')
    WHEN NEW.signal_sources != OLD.signal_sources
      THEN RAISE(ABORT, 'epochs: signal_sources are frozen in active epoch')
    WHEN NEW.scoring_thresholds != OLD.scoring_thresholds
      THEN RAISE(ABORT, 'epochs: scoring_thresholds are frozen in active epoch')
    WHEN NEW.anomaly_thresholds != OLD.anomaly_thresholds
      THEN RAISE(ABORT, 'epochs: anomaly_thresholds are frozen in active epoch')
  END;
END;

-- One active epoch per wizard scope (NULL = global)
CREATE UNIQUE INDEX IF NOT EXISTS idx_epochs_one_active_global
ON epochs(wizard_id) WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_epochs_status ON epochs(status);

-- ============================================================
-- PROMPT VERSION REGISTRY
-- ============================================================

CREATE TABLE IF NOT EXISTS prompt_versions (
  id              TEXT PRIMARY KEY,
  -- e.g. 'scout_extraction_v1.0'

  agent_role      TEXT NOT NULL
    CHECK(agent_role IN ('scout','validator','skeptic','curator','wizard')),
  version         TEXT NOT NULL,
  prompt_hash     TEXT NOT NULL UNIQUE,
  -- SHA256 of prompt content — immutable fingerprint
  prompt_content  TEXT NOT NULL,
  -- Full prompt stored permanently

  created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  created_by      TEXT NOT NULL,
  notes           TEXT,

  UNIQUE(agent_role, version)
);

-- Immutable: content cannot change after registration
CREATE TRIGGER IF NOT EXISTS prompt_versions_immutability
BEFORE UPDATE OF prompt_hash, prompt_content ON prompt_versions
BEGIN
  SELECT RAISE(ABORT, 'prompt_versions: content is immutable after registration');
END;

-- ============================================================
-- CYCLE VITALITY
-- ============================================================

CREATE TABLE IF NOT EXISTS cycle_vitality (
  id                          TEXT PRIMARY KEY,
  -- Format: 'cvit_' || ulid()

  wizard_id                   TEXT NOT NULL REFERENCES wizards(id),
  wizard_domain               TEXT NOT NULL,
  epoch_id                    TEXT NOT NULL REFERENCES epochs(id),

  -- Timing
  started_at                  TEXT NOT NULL,
  completed_at                TEXT,
  duration_seconds            INTEGER,

  -- Status
  cycle_status                TEXT NOT NULL DEFAULT 'running'
    CHECK(cycle_status IN ('running','completed','failed','aborted')),
  failure_reason              TEXT,

  -- Activity Metrics
  sources_scanned             INTEGER NOT NULL DEFAULT 0,
  raw_items_ingested          INTEGER NOT NULL DEFAULT 0,
  raw_items_duplicate         INTEGER NOT NULL DEFAULT 0,
  atoms_proposed              INTEGER NOT NULL DEFAULT 0,
  atoms_accepted              INTEGER NOT NULL DEFAULT 0,
  atoms_rejected              INTEGER NOT NULL DEFAULT 0,
  atoms_duplicate             INTEGER NOT NULL DEFAULT 0,
  counter_evidence_proposed   INTEGER NOT NULL DEFAULT 0,
  pattern_updates_proposed    INTEGER NOT NULL DEFAULT 0,
  cross_domain_references     INTEGER NOT NULL DEFAULT 0,

  -- Quality Signals (computed)
  acceptance_rate             REAL,
  -- atoms_accepted / atoms_proposed
  duplicate_rate              REAL,
  -- duplicates / total attempted

  -- Anomaly
  anomaly_flags               TEXT NOT NULL DEFAULT '[]',
  -- JSON array of { threshold_name, severity, detail }
  anomaly_severity            TEXT NOT NULL DEFAULT 'none'
    CHECK(anomaly_severity IN ('none','warning','critical')),

  -- Cost
  model_id                    TEXT NOT NULL,
  total_tokens                INTEGER NOT NULL DEFAULT 0,
  estimated_cost_usd          REAL NOT NULL DEFAULT 0.0,

  created_at                  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_cvit_wizard   ON cycle_vitality(wizard_id);
CREATE INDEX IF NOT EXISTS idx_cvit_epoch    ON cycle_vitality(epoch_id);
CREATE INDEX IF NOT EXISTS idx_cvit_anomaly  ON cycle_vitality(anomaly_severity);
CREATE INDEX IF NOT EXISTS idx_cvit_started  ON cycle_vitality(started_at);

-- ============================================================
-- GOVERNANCE ACTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS governance_actions (
  id                  TEXT PRIMARY KEY,

  action_type         TEXT NOT NULL
    CHECK(action_type IN (
      'log_and_monitor','notify_operator','halt_wizard',
      'emergency_halt','god_redirect','god_approve_structural',
      'god_reject_pattern','epoch_change','wizard_activated',
      'wizard_suspended','manual_audit_triggered'
    )),

  wizard_id           TEXT REFERENCES wizards(id),
  cycle_vitality_id   TEXT REFERENCES cycle_vitality(id),
  pattern_id          TEXT,
  -- Reference to knowledge.db patterns (no FK across DBs)

  triggered_by        TEXT NOT NULL,
  -- anomaly_threshold name or 'human' or 'king'
  triggered_at        TEXT NOT NULL,

  -- Resolution
  resolved_at         TEXT,
  resolved_by         TEXT,
  resolution_notes    TEXT,

  status              TEXT NOT NULL DEFAULT 'open'
    CHECK(status IN ('open','acknowledged','resolved','escalated')),

  -- God-mode actions store additional context
  god_instruction     TEXT,
  -- For god_redirect: the instruction given to the wizard
  god_rationale       TEXT,
  -- For approve/reject: rationale documented

  created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_gov_wizard  ON governance_actions(wizard_id);
CREATE INDEX IF NOT EXISTS idx_gov_status  ON governance_actions(status);
CREATE INDEX IF NOT EXISTS idx_gov_type    ON governance_actions(action_type);

-- ============================================================
-- HUMAN OPERATORS (God registry)
-- ============================================================

CREATE TABLE IF NOT EXISTS operators (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  role        TEXT NOT NULL DEFAULT 'king'
    CHECK(role IN ('king','overseer','observer')),
  -- god: full permissions including STRUCTURAL promotion
  -- overseer: can review and redirect, cannot promote to STRUCTURAL
  -- observer: read-only
  active      INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- ============================================================
-- WIZARD MEMORY & EVOLUTION
-- [ZUKUNFT — Phase 6+]
-- Schema schon jetzt angelegt damit nichts verloren geht.
-- Tabellen werden in Phase 6 aktiviert.
-- ============================================================

CREATE TABLE IF NOT EXISTS wizard_memory (
  id              TEXT PRIMARY KEY,
  wizard_id       TEXT NOT NULL REFERENCES wizards(id),

  -- Was gelernt wurde
  memory_type     TEXT NOT NULL
    CHECK(memory_type IN (
      'success',        -- Pattern erfolgreich promoted
      'failure',        -- Atom/Pattern war falsch
      'domain_insight', -- Erkenntnis über die eigene Domain
      'method_insight', -- Erkenntnis über Extraktionsmethoden
      'collaboration'   -- Erkenntnis aus Zusammenarbeit mit anderem Wizard
    )),
  description     TEXT NOT NULL,
  -- Was ist passiert

  impact          TEXT NOT NULL,
  -- Wie ändert das zukünftiges Verhalten

  -- Referenz
  atom_id         TEXT,
  -- Wenn relevant
  pattern_id      TEXT,
  -- Wenn relevant
  epoch_id        TEXT NOT NULL REFERENCES epochs(id),

  created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS wizard_career_history (
  id              TEXT PRIMARY KEY,
  wizard_id       TEXT NOT NULL REFERENCES wizards(id),

  level_from      TEXT NOT NULL,
  level_to        TEXT NOT NULL,
  -- junior_librarian | librarian | senior_librarian | domain_lead | master

  promoted_at     TEXT NOT NULL,
  promoted_by     TEXT NOT NULL DEFAULT 'op_king_001',
  -- Immer durch den King

  reason          TEXT NOT NULL,
  -- Warum Beförderung verdient

  new_capabilities TEXT NOT NULL DEFAULT '[]',
  -- JSON array: was darf er jetzt mehr
  new_budget_multiplier REAL NOT NULL DEFAULT 1.0,
  -- Budget-Faktor nach Beförderung

  epoch_id        TEXT NOT NULL REFERENCES epochs(id),
  created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS wizard_functional_state (
  id              TEXT PRIMARY KEY,
  wizard_id       TEXT NOT NULL REFERENCES wizards(id),

  -- Funktionale Zustände (kein echter Bias — aber Verhaltensmuster)
  confidence_level    REAL NOT NULL DEFAULT 0.5
    CHECK(confidence_level BETWEEN 0.0 AND 1.0),
  -- Steigt bei erfolgreichen Promotionen, sinkt bei Fehlern

  caution_level       REAL NOT NULL DEFAULT 0.5
    CHECK(caution_level BETWEEN 0.0 AND 1.0),
  -- Steigt nach widerlegten Patterns

  curiosity_domains   TEXT NOT NULL DEFAULT '[]',
  -- JSON array: Domänen die gerade interessant erscheinen

  last_updated    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  epoch_id        TEXT NOT NULL REFERENCES epochs(id),

  UNIQUE(wizard_id)
  -- Ein State-Record pro Wizard
);

CREATE TABLE IF NOT EXISTS wizard_reproduction (
  id              TEXT PRIMARY KEY,

  -- Mentor → Junior Beziehung
  mentor_wizard_id  TEXT NOT NULL REFERENCES wizards(id),
  junior_wizard_id  TEXT NOT NULL REFERENCES wizards(id),

  approved_by     TEXT NOT NULL DEFAULT 'op_king_001',
  approved_at     TEXT NOT NULL,
  rationale       TEXT NOT NULL,
  -- Warum hat der Mentor einen Junior verdient

  -- Vererbung
  inherited_domain      TEXT NOT NULL,
  inherited_persona_dna TEXT NOT NULL,
  -- Welche Aspekte des Mentors wurden vererbt

  own_personality TEXT NOT NULL,
  -- Was ist am Junior anders/eigen

  status          TEXT NOT NULL DEFAULT 'active'
    CHECK(status IN ('active','graduated','retired')),
  -- graduated = Junior ist selbst Senior geworden

  created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_wiz_memory_wizard   ON wizard_memory(wizard_id);
CREATE INDEX IF NOT EXISTS idx_wiz_career_wizard   ON wizard_career_history(wizard_id);
CREATE INDEX IF NOT EXISTS idx_wiz_repro_mentor    ON wizard_reproduction(mentor_wizard_id);
CREATE INDEX IF NOT EXISTS idx_wiz_repro_junior    ON wizard_reproduction(junior_wizard_id);
