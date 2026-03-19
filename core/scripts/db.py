"""
OHARA — Database Connection & Core Utilities
All DB access goes through this module. Never connect directly.
"""

import sqlite3
import hashlib
import json
import time
import random
import string
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

BASE_DIR = Path(__file__).parent.parent.parent
DB_DIR = BASE_DIR / "core" / "db"

VAULT_DB      = DB_DIR / "ohara_vault.db"
KNOWLEDGE_DB  = DB_DIR / "ohara_knowledge.db"
GOVERNANCE_DB = DB_DIR / "ohara_governance.db"

# ============================================================
# CONNECTION FACTORY
# ============================================================

def _connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise RuntimeError(
            f"Database not found: {db_path}\n"
            f"Run: python core/db/migrations/migrate.py"
        )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def vault_db()      -> sqlite3.Connection: return _connect(VAULT_DB)
def knowledge_db()  -> sqlite3.Connection: return _connect(KNOWLEDGE_DB)
def governance_db() -> sqlite3.Connection: return _connect(GOVERNANCE_DB)

# ============================================================
# ID GENERATION
# ============================================================

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def ulid(prefix: str = "") -> str:
    """Time-sortable unique ID. Not spec-compliant ULID but sufficient for Phase 1."""
    ts = hex(int(time.time() * 1000))[2:]
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{prefix}{ts}{rand}"

def atom_id(claim: str, source_ids: list[str], epoch_id: str) -> str:
    claim_norm = claim.strip().lower()
    source_hash = source_hash_set(source_ids)
    return "atom_" + sha256(claim_norm + source_hash + epoch_id)[:24]

def source_hash_set(source_ids: list[str]) -> str:
    return sha256(json.dumps(sorted(source_ids)))

def raw_item_id(content: bytes) -> str:
    return "raw_" + sha256_bytes(content)[:32]

# ============================================================
# TIME
# ============================================================

def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ============================================================
# ACTIVE EPOCH
# ============================================================

def get_active_epoch(wizard_id: Optional[str] = None) -> dict:
    """Get the active epoch. Wizard-scoped first, then global fallback."""
    conn = governance_db()
    try:
        if wizard_id:
            row = conn.execute(
                "SELECT * FROM epochs WHERE wizard_id=? AND status='active'",
                (wizard_id,)
            ).fetchone()
            if row:
                return dict(row)
        row = conn.execute(
            "SELECT * FROM epochs WHERE wizard_id IS NULL AND status='active'"
        ).fetchone()
        if not row:
            raise RuntimeError("No active epoch found. Run seed.py first.")
        return dict(row)
    finally:
        conn.close()

# ============================================================
# WIZARD LOOKUP
# ============================================================

def get_wizard(short_name: str) -> Optional[dict]:
    conn = governance_db()
    try:
        row = conn.execute(
            "SELECT * FROM wizards WHERE short_name=? AND status='active'",
            (short_name,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def list_active_wizards() -> list[dict]:
    conn = governance_db()
    try:
        rows = conn.execute(
            "SELECT * FROM wizards WHERE status='active' ORDER BY short_name"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

# ============================================================
# VAULT HELPERS
# ============================================================

def raw_item_exists(content_hash: str) -> bool:
    conn = vault_db()
    try:
        row = conn.execute(
            "SELECT 1 FROM raw_items WHERE content_hash=?", (content_hash,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()

def insert_raw_item(
    origin_url: str,
    domain: str,
    content: bytes,
    content_type: str,
    source_tier: str,
    ingestion_agent: str,
    epoch_id: str,
    editorial_independence: float = 0.5,
) -> tuple[str, bool]:
    """
    Insert a raw item. Returns (raw_item_id, is_new).
    If content already exists (dedup), returns existing id and is_new=False.
    """
    content_hash = sha256_bytes(content)
    item_id = "raw_" + content_hash[:32]

    if raw_item_exists(content_hash):
        return item_id, False

    # Store content to filesystem
    vault_path = BASE_DIR / "core" / "vault" / "raw"
    date_path = vault_path / now()[:10].replace("-", "/")
    date_path.mkdir(parents=True, exist_ok=True)
    content_file = date_path / f"{content_hash}.bin"
    content_file.write_bytes(content)
    relative_path = str(content_file.relative_to(BASE_DIR))

    conn = vault_db()
    try:
        conn.execute("""
            INSERT INTO raw_items (
                id, origin_url, domain, ingested_at, epoch_id, ingestion_agent,
                content_type, content_hash, content_path, content_size_bytes,
                source_tier, editorial_independence_score, processing_status
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            item_id, origin_url, domain, now(), epoch_id, ingestion_agent,
            content_type, content_hash, relative_path, len(content),
            source_tier, editorial_independence, "pending"
        ))
        conn.commit()
        return item_id, True
    finally:
        conn.close()

# ============================================================
# KNOWLEDGE HELPERS
# ============================================================

def insert_atom(
    claim: str,
    claim_type: str,
    domain: str,
    source_ids: list[str],
    epoch_id: str,
    model_id: str,
    extracted_by: str,
    speculation_level: int,
    confidence_score: float,
    cross_domain_tags: list[str] = None,
    utility_vector: list[str] = None,
    extraction_parameters: dict = None,
    temporal_first_seen: str = None,
) -> tuple[str, bool]:
    """
    Insert an atom. Returns (atom_id, is_new).
    Content-addressed: same claim+sources+epoch = same ID (dedup).
    """
    src_hash = source_hash_set(source_ids)
    a_id = atom_id(claim, source_ids, epoch_id)

    conn = knowledge_db()
    try:
        existing = conn.execute("SELECT id FROM atoms WHERE id=?", (a_id,)).fetchone()
        if existing:
            return a_id, False

        conn.execute("""
            INSERT INTO atoms (
                id, claim, claim_type, domain, cross_domain_tags,
                utility_vector,
                source_ids, source_hash_set, epoch_id, model_id,
                extraction_parameters, extracted_by, extracted_at,
                speculation_level, confidence_score, status,
                temporal_first_seen
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            a_id, claim, claim_type, domain,
            json.dumps(cross_domain_tags or []),
            json.dumps(utility_vector or []),
            json.dumps(source_ids), src_hash, epoch_id, model_id,
            json.dumps(extraction_parameters or {}), extracted_by, now(),
            speculation_level, confidence_score, "candidate",
            temporal_first_seen or now()
        ))
        conn.commit()
        return a_id, True
    finally:
        conn.close()

def get_atom(atom_id: str) -> Optional[dict]:
    conn = knowledge_db()
    try:
        row = conn.execute("SELECT * FROM atoms WHERE id=?", (atom_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def list_atoms(domain: str = None, status: str = None, limit: int = 50) -> list[dict]:
    conn = knowledge_db()
    try:
        q = "SELECT * FROM atoms WHERE 1=1"
        params = []
        if domain:
            q += " AND domain=?"
            params.append(domain)
        if status:
            q += " AND status=?"
            params.append(status)
        q += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in conn.execute(q, params).fetchall()]
    finally:
        conn.close()

def accept_atom(atom_id: str, reviewer: str) -> None:
    conn = knowledge_db()
    try:
        conn.execute(
            "UPDATE atoms SET status='accepted' WHERE id=? AND status='candidate'",
            (atom_id,)
        )
        conn.commit()
    finally:
        conn.close()

def reject_atom(atom_id: str, reason: str, reviewer: str) -> None:
    conn = knowledge_db()
    try:
        conn.execute(
            "UPDATE atoms SET status='rejected', rejection_reason=? WHERE id=?",
            (reason, atom_id)
        )
        conn.commit()
    finally:
        conn.close()

def list_patterns(domain: str = None, status: str = None) -> list[dict]:
    conn = knowledge_db()
    try:
        q = "SELECT * FROM patterns WHERE 1=1"
        params = []
        if domain:
            q += " AND domain=?"
            params.append(domain)
        if status:
            q += " AND status=?"
            params.append(status)
        q += " ORDER BY status_changed_at DESC"
        return [dict(r) for r in conn.execute(q, params).fetchall()]
    finally:
        conn.close()

# ============================================================
# STATS
# ============================================================

def library_stats() -> dict:
    stats = {}

    v = vault_db()
    stats["raw_items_total"] = v.execute("SELECT COUNT(*) FROM raw_items").fetchone()[0]
    stats["raw_items_processed"] = v.execute(
        "SELECT COUNT(*) FROM raw_items WHERE processing_status='processed'"
    ).fetchone()[0]
    v.close()

    k = knowledge_db()
    stats["atoms_total"] = k.execute("SELECT COUNT(*) FROM atoms").fetchone()[0]
    stats["atoms_accepted"] = k.execute(
        "SELECT COUNT(*) FROM atoms WHERE status='accepted'"
    ).fetchone()[0]
    stats["atoms_candidate"] = k.execute(
        "SELECT COUNT(*) FROM atoms WHERE status='candidate'"
    ).fetchone()[0]
    stats["patterns_by_status"] = {
        r[0]: r[1] for r in k.execute(
            "SELECT status, COUNT(*) FROM patterns GROUP BY status"
        ).fetchall()
    }
    stats["books_total"] = k.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    stats["counter_evidence_unresolved"] = k.execute(
        "SELECT COUNT(*) FROM counter_evidence WHERE resolution_status='unresolved'"
    ).fetchone()[0]
    k.close()

    return stats
