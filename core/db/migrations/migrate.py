#!/usr/bin/env python3
"""
OHARA Database Migration Runner
Initializes all three databases from schema files.
Run once on fresh setup. Safe to re-run (IF NOT EXISTS guards).
"""

import sqlite3
import os
import sys
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
SCHEMA_DIR = BASE_DIR / "core" / "db" / "schema"
DB_DIR = BASE_DIR / "core" / "db"

DATABASES = {
    "ohara_vault.db": "vault.sql",
    "ohara_knowledge.db": "knowledge.sql",
    "ohara_governance.db": "governance.sql",
}

def run_migration(db_name: str, schema_file: str) -> None:
    db_path = DB_DIR / db_name
    schema_path = SCHEMA_DIR / schema_file

    if not schema_path.exists():
        print(f"  ERROR: Schema file not found: {schema_path}")
        sys.exit(1)

    schema_sql = schema_path.read_text()
    schema_hash = hashlib.sha256(schema_sql.encode()).hexdigest()[:8]

    print(f"\n  [{db_name}]")
    print(f"  Schema: {schema_file} (hash: {schema_hash})")

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print(f"  Status: OK — {db_path}")
    except Exception as e:
        print(f"  FAILED: {e}")
        conn.close()
        sys.exit(1)
    finally:
        conn.close()

def verify_migration(db_name: str, expected_tables: list[str]) -> None:
    db_path = DB_DIR / db_name
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    actual_tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    missing = set(expected_tables) - actual_tables
    if missing:
        print(f"  VERIFICATION FAILED — missing tables: {missing}")
        sys.exit(1)
    print(f"  Verified: {len(actual_tables)} tables present")

if __name__ == "__main__":
    print("=" * 60)
    print("OHARA — Database Migration")
    print("=" * 60)

    DB_DIR.mkdir(parents=True, exist_ok=True)

    for db_name, schema_file in DATABASES.items():
        run_migration(db_name, schema_file)

    print("\n  Verifying schema integrity...")

    verify_migration("ohara_vault.db", ["raw_items"])
    verify_migration("ohara_knowledge.db", [
        "atoms", "patterns", "pattern_history",
        "counter_evidence", "skeptic_cycles",
        "books", "book_pattern_dependencies",
        "cross_domain_references"
    ])
    verify_migration("ohara_governance.db", [
        "wizards", "epochs", "prompt_versions",
        "cycle_vitality", "governance_actions", "operators"
    ])

    print("\n" + "=" * 60)
    print("Migration complete. All databases initialized.")
    print("Next: python core/db/seed/seed.py")
    print("=" * 60)
