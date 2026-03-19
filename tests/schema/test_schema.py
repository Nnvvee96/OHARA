#!/usr/bin/env python3
"""
OHARA Schema Acceptance Tests
Tests all invariants and constraints from tdd.md §7.
ALL 34 TESTS MUST PASS. Zero failures permitted for Phase 0 exit gate.
"""

import sqlite3
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent.parent
DB_DIR = BASE_DIR / "core" / "db"

VAULT_DB    = DB_DIR / "ohara_vault.db"
KNOWLEDGE_DB = DB_DIR / "ohara_knowledge.db"
GOVERN_DB   = DB_DIR / "ohara_governance.db"

passed = 0
failed = 0
results = []

def test(name: str, fn) -> None:
    global passed, failed
    try:
        fn()
        passed += 1
        results.append(("PASS", name))
    except AssertionError as e:
        failed += 1
        results.append(("FAIL", f"{name} — {e}"))
    except Exception as e:
        failed += 1
        results.append(("FAIL", f"{name} — UNEXPECTED: {e}"))

def expect_raises(conn, sql, params=(), msg_contains=""):
    try:
        conn.execute(sql, params)
        conn.commit()
        raise AssertionError(f"Expected exception but none raised. msg_contains='{msg_contains}'")
    except sqlite3.IntegrityError as e:
        if msg_contains and msg_contains.lower() not in str(e).lower():
            raise AssertionError(f"Wrong error: {e}")
    except sqlite3.OperationalError as e:
        if msg_contains and msg_contains.lower() not in str(e).lower():
            raise AssertionError(f"Wrong error: {e}")

def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
EPOCH_ID = "epoch_20260221_cal0"

# ============================================================
# VAULT TESTS (raw_items)
# ============================================================

def test_vault_insert_basic():
    conn = sqlite3.connect(VAULT_DB)
    content = b"test content alpha"
    content_hash = sha(content.decode())
    raw_id = "raw_" + content_hash[:16]
    conn.execute("""
        INSERT OR IGNORE INTO raw_items (
            id, origin_url, domain, ingested_at, epoch_id, ingestion_agent,
            content_type, content_hash, content_path, content_size_bytes,
            source_tier, processing_status
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (raw_id, "https://example.com/a", "ai_patterns", NOW, EPOCH_ID,
          "human", "text", content_hash, f"vault/raw/{content_hash}.bin",
          len(content), "primary", "pending"))
    conn.commit()
    row = conn.execute("SELECT id FROM raw_items WHERE id=?", (raw_id,)).fetchone()
    assert row is not None, "Insert failed"
    conn.close()

def test_vault_immutability_origin_url():
    conn = sqlite3.connect(VAULT_DB)
    content_hash = sha("test content alpha")
    raw_id = "raw_" + content_hash[:16]
    expect_raises(
        conn,
        "UPDATE raw_items SET origin_url=? WHERE id=?",
        ("https://evil.com", raw_id),
        "origin_url is immutable"
    )
    conn.close()

def test_vault_immutability_content_hash():
    conn = sqlite3.connect(VAULT_DB)
    content_hash = sha("test content alpha")
    raw_id = "raw_" + content_hash[:16]
    expect_raises(
        conn,
        "UPDATE raw_items SET content_hash=? WHERE id=?",
        ("fakehash", raw_id),
        "content_hash is immutable"
    )
    conn.close()

def test_vault_no_delete():
    conn = sqlite3.connect(VAULT_DB)
    content_hash = sha("test content alpha")
    raw_id = "raw_" + content_hash[:16]
    expect_raises(
        conn,
        "DELETE FROM raw_items WHERE id=?",
        (raw_id,),
        "deletion is forbidden"
    )
    conn.close()

def test_vault_duplicate_content_hash():
    conn = sqlite3.connect(VAULT_DB)
    content_hash = sha("test content alpha")
    expect_raises(
        conn,
        """INSERT INTO raw_items (
            id, origin_url, domain, ingested_at, epoch_id, ingestion_agent,
            content_type, content_hash, content_path, content_size_bytes,
            source_tier, processing_status
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("raw_different_id", "https://other.com", "ai_patterns", NOW, EPOCH_ID,
         "human", "text", content_hash, "vault/raw/x.bin", 10, "primary", "pending"),
        "UNIQUE"
    )
    conn.close()

def test_vault_status_update_allowed():
    conn = sqlite3.connect(VAULT_DB)
    content_hash = sha("test content alpha")
    raw_id = "raw_" + content_hash[:16]
    conn.execute("UPDATE raw_items SET processing_status=? WHERE id=?", ("processed", raw_id))
    conn.commit()
    row = conn.execute("SELECT processing_status FROM raw_items WHERE id=?", (raw_id,)).fetchone()
    assert row[0] == "processed", "Status update should be allowed"
    conn.close()

# ============================================================
# KNOWLEDGE TESTS (atoms)
# ============================================================

def _insert_test_atom(conn, claim="Test claim under 280 chars.", suffix=""):
    claim_norm = claim.strip().lower()
    source_ids = json.dumps(["raw_abc123"])
    source_hash = sha(json.dumps(sorted(["raw_abc123"])))
    atom_id = "atom_" + sha(claim_norm + source_hash + EPOCH_ID + suffix)[:16]
    conn.execute("""
        INSERT OR IGNORE INTO atoms (
            id, claim, claim_type, domain, source_ids, source_hash_set,
            epoch_id, model_id, extraction_parameters, extracted_by,
            extracted_at, speculation_level, confidence_score, status
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        atom_id, claim, "observation", "ai_patterns",
        source_ids, source_hash, EPOCH_ID,
        "claude-sonnet-4-6", json.dumps({"prompt_version": "v1.0"}),
        "human", NOW, 2, 0.7, "candidate"
    ))
    conn.commit()
    return atom_id

def test_atom_insert_basic():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    atom_id = _insert_test_atom(conn, "Basic valid atom claim for testing.", "a1")
    row = conn.execute("SELECT id FROM atoms WHERE id=?", (atom_id,)).fetchone()
    assert row is not None, "Atom insert failed"
    conn.close()

def test_atom_claim_too_long():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    long_claim = "x" * 281
    source_hash = sha(json.dumps(["raw_abc123"]))
    atom_id = "atom_toolong"
    expect_raises(
        conn,
        """INSERT INTO atoms (
            id, claim, claim_type, domain, source_ids, source_hash_set,
            epoch_id, model_id, extraction_parameters, extracted_by,
            extracted_at, speculation_level, confidence_score, status
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (atom_id, long_claim, "observation", "ai_patterns",
         json.dumps(["raw_abc123"]), source_hash, EPOCH_ID,
         "claude-sonnet-4-6", "{}", "human", NOW, 2, 0.7, "candidate"),
        "claim_length"
    )
    conn.close()

def test_atom_empty_source_ids():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    expect_raises(
        conn,
        """INSERT INTO atoms (
            id, claim, claim_type, domain, source_ids, source_hash_set,
            epoch_id, model_id, extraction_parameters, extracted_by,
            extracted_at, speculation_level, confidence_score, status
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("atom_nosrc", "Valid claim", "observation", "ai_patterns",
         "[]", sha("[]"), EPOCH_ID,
         "claude-sonnet-4-6", "{}", "human", NOW, 2, 0.7, "candidate"),
        "source_ids_not_empty"
    )
    conn.close()

def test_atom_superseded_requires_pointer():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    atom_id = _insert_test_atom(conn, "Atom to be superseded test.", "sup1")
    expect_raises(
        conn,
        "UPDATE atoms SET status='superseded' WHERE id=?",
        (atom_id,),
        "superseded_requires_pointer"
    )
    conn.close()

def test_atom_rejected_requires_reason():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    atom_id = _insert_test_atom(conn, "Atom to be rejected test.", "rej1")
    expect_raises(
        conn,
        "UPDATE atoms SET status='rejected' WHERE id=?",
        (atom_id,),
        "rejected_requires_reason"
    )
    conn.close()

def test_atom_no_delete():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    atom_id = _insert_test_atom(conn, "Atom that cannot be deleted.", "del1")
    expect_raises(
        conn,
        "DELETE FROM atoms WHERE id=?",
        (atom_id,),
        "deletion forbidden"
    )
    conn.close()

def test_atom_superseded_with_pointer():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    atom1 = _insert_test_atom(conn, "Original atom v1 for supersede test.", "sv1")
    atom2 = _insert_test_atom(conn, "Replacement atom v2 for supersede test.", "sv2")
    conn.execute(
        "UPDATE atoms SET status='superseded', superseded_by=? WHERE id=?",
        (atom2, atom1)
    )
    conn.commit()
    row = conn.execute("SELECT status, superseded_by FROM atoms WHERE id=?", (atom1,)).fetchone()
    assert row[0] == "superseded" and row[1] == atom2, "Supersede with pointer should work"
    conn.close()

# ============================================================
# KNOWLEDGE TESTS (counter_evidence + patterns)
# ============================================================

def _insert_test_pattern(conn, title="Test Pattern Alpha"):
    pat_id = "pat_test_" + sha(title)[:8]
    conn.execute("""
        INSERT OR IGNORE INTO patterns (
            id, title, summary, domain, status, status_changed_at,
            source_hash_set, epoch_id, created_by, updated_by
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        pat_id, title, "Test pattern summary under 500 chars.",
        "ai_patterns", "signal", NOW,
        sha("test"), EPOCH_ID, "human", "human"
    ))
    conn.commit()
    return pat_id

def test_counter_evidence_updates_pattern_count():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    atom_id = _insert_test_atom(conn, "CE test atom claim here.", "ce1")
    pat_id = _insert_test_pattern(conn, "Pattern For CE Count Test")

    ce_id = "ce_test_001"
    conn.execute("""
        INSERT OR IGNORE INTO counter_evidence (
            id, atom_id, contradicts_pattern_id, severity,
            resolution_status, epoch_id, proposed_by
        ) VALUES (?,?,?,?,?,?,?)
    """, (ce_id, atom_id, pat_id, "strong", "unresolved", EPOCH_ID, "human"))
    conn.commit()

    row = conn.execute(
        "SELECT unresolved_strong_count, counter_evidence_count FROM patterns WHERE id=?",
        (pat_id,)
    ).fetchone()
    assert row[0] == 1, f"unresolved_strong_count should be 1, got {row[0]}"
    assert row[1] == 1, f"counter_evidence_count should be 1, got {row[1]}"
    conn.close()

def test_counter_evidence_resolves_updates_count():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    pat_id = _insert_test_pattern(conn, "Pattern For CE Resolution Test")
    atom_id = _insert_test_atom(conn, "CE resolution test atom.", "cer1")

    ce_id = "ce_test_resolve_001"
    conn.execute("""
        INSERT OR IGNORE INTO counter_evidence (
            id, atom_id, contradicts_pattern_id, severity,
            resolution_status, epoch_id, proposed_by
        ) VALUES (?,?,?,?,?,?,?)
    """, (ce_id, atom_id, pat_id, "strong", "unresolved", EPOCH_ID, "human"))
    conn.commit()

    conn.execute("""
        UPDATE counter_evidence
        SET resolution_status='acknowledged', resolved_by='human', resolved_at=?
        WHERE id=?
    """, (NOW, ce_id))
    conn.commit()

    row = conn.execute(
        "SELECT unresolved_strong_count FROM patterns WHERE id=?", (pat_id,)
    ).fetchone()
    assert row[0] == 0, f"unresolved_strong_count should be 0 after resolution, got {row[0]}"
    conn.close()

def test_ce_refuted_requires_rationale():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    pat_id = _insert_test_pattern(conn, "Pattern CE Refute Rationale Test")
    atom_id = _insert_test_atom(conn, "CE refuted rationale test atom.", "crr1")
    ce_id = "ce_refute_no_rat"
    conn.execute("""
        INSERT OR IGNORE INTO counter_evidence (
            id, atom_id, contradicts_pattern_id, severity,
            resolution_status, epoch_id, proposed_by
        ) VALUES (?,?,?,?,?,?,?)
    """, (ce_id, atom_id, pat_id, "moderate", "unresolved", EPOCH_ID, "human"))
    conn.commit()

    expect_raises(
        conn,
        "UPDATE counter_evidence SET resolution_status='refuted', resolved_by='human' WHERE id=?",
        (ce_id,),
        "refuted_requires_rationale"
    )
    conn.close()

def test_pattern_structural_requires_human_fields():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    pat_id = _insert_test_pattern(conn, "Pattern Structural No Human Test")
    expect_raises(
        conn,
        "UPDATE patterns SET status='structural' WHERE id=?",
        (pat_id,),
        "structural_requires_human"
    )
    conn.close()

def test_pattern_structural_rationale_min_length():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    pat_id = _insert_test_pattern(conn, "Pattern Structural Short Rationale")
    expect_raises(
        conn,
        """UPDATE patterns SET status='structural',
           structural_approved_by='op_god_001',
           structural_approved_at=?,
           structural_rationale=?
           WHERE id=?""",
        (NOW, "Too short.", pat_id),
        "structural_requires_human"
    )
    conn.close()

def test_pattern_structural_with_full_fields():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    pat_id = _insert_test_pattern(conn, "Pattern Structural Full Fields Test")
    long_rationale = "This pattern has been validated across multiple sources and time periods. " \
                     "Cross-domain resonance confirmed. Skeptic cycle completed. " \
                     "No unresolved strong counter-evidence. Human approved."
    conn.execute("""
        UPDATE patterns SET status='structural',
            structural_approved_by='op_god_001',
            structural_approved_at=?,
            structural_rationale=?
        WHERE id=?
    """, (NOW, long_rationale, pat_id))
    conn.commit()
    row = conn.execute("SELECT status FROM patterns WHERE id=?", (pat_id,)).fetchone()
    assert row[0] == "structural", "Structural promotion with full fields should succeed"
    conn.close()

def test_pattern_no_delete():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    pat_id = _insert_test_pattern(conn, "Pattern No Delete Test")
    expect_raises(
        conn,
        "DELETE FROM patterns WHERE id=?",
        (pat_id,),
        "deletion forbidden"
    )
    conn.close()

def test_pattern_deprecation_requires_reason():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    pat_id = _insert_test_pattern(conn, "Pattern Deprecation Reason Test")
    expect_raises(
        conn,
        "UPDATE patterns SET status='deprecated' WHERE id=?",
        (pat_id,),
        "deprecation_requires_reason"
    )
    conn.close()

# ============================================================
# BOOK / DEPENDENCY TESTS
# ============================================================

def _insert_test_book(conn, title="Test Book Alpha"):
    book_id = "book_test_" + sha(title)[:8]
    conn.execute("""
        INSERT OR IGNORE INTO books (
            id, title, domain, description, status,
            epoch_id, source_hash_set, created_by, updated_by
        ) VALUES (?,?,?,?,?,?,?,?,?)
    """, (book_id, title, "ai_patterns", "Test book description.",
          "draft", EPOCH_ID, sha("test"), "human", "human"))
    conn.commit()
    return book_id

def test_book_pattern_dep_staleness_on_deprecation():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    pat_id = _insert_test_pattern(conn, "Pattern For Staleness Test")
    book_id = _insert_test_book(conn, "Book For Staleness Test")

    dep_id = "bpd_stale_test_001"
    conn.execute("""
        INSERT OR IGNORE INTO book_pattern_dependencies (
            id, book_id, pattern_id, pattern_version_snapshot,
            pattern_status_at_inclusion, pattern_confidence_at_inclusion,
            staleness_status, included_by
        ) VALUES (?,?,?,?,?,?,?,?)
    """, (dep_id, book_id, pat_id, 1, "validated", 0.75, "current", "human"))
    conn.commit()

    conn.execute("""
        UPDATE patterns SET status='deprecated', deprecated_reason='Test deprecation'
        WHERE id=?
    """, (pat_id,))
    conn.commit()

    row = conn.execute(
        "SELECT staleness_status FROM book_pattern_dependencies WHERE id=?",
        (dep_id,)
    ).fetchone()
    assert row[0] == "deprecated_dependency", \
        f"Staleness should be deprecated_dependency, got {row[0]}"

    book_row = conn.execute(
        "SELECT stale_dependency_count FROM books WHERE id=?", (book_id,)
    ).fetchone()
    assert book_row[0] == 1, f"stale_dependency_count should be 1, got {book_row[0]}"
    conn.close()

# ============================================================
# GOVERNANCE TESTS (epochs, prompts)
# ============================================================

def test_epoch_frozen_model_id():
    conn = sqlite3.connect(GOVERN_DB)
    expect_raises(
        conn,
        "UPDATE epochs SET model_id=? WHERE id=?",
        ("gpt-5", EPOCH_ID),
        "model_id is frozen"
    )
    conn.close()

def test_epoch_frozen_prompt_version():
    conn = sqlite3.connect(GOVERN_DB)
    expect_raises(
        conn,
        "UPDATE epochs SET extraction_prompt_version=? WHERE id=?",
        ("scout_extraction_v9.9", EPOCH_ID),
        "extraction_prompt_version is frozen"
    )
    conn.close()

def test_epoch_frozen_scoring_thresholds():
    conn = sqlite3.connect(GOVERN_DB)
    expect_raises(
        conn,
        "UPDATE epochs SET scoring_thresholds=? WHERE id=?",
        (json.dumps({"hacked": True}), EPOCH_ID),
        "scoring_thresholds are frozen"
    )
    conn.close()

def test_prompt_version_immutability():
    conn = sqlite3.connect(GOVERN_DB)
    expect_raises(
        conn,
        "UPDATE prompt_versions SET prompt_content=? WHERE id=?",
        ("hacked content", "scout_extraction_v1.0"),
        "content is immutable"
    )
    conn.close()

def test_prompt_version_hash_immutability():
    conn = sqlite3.connect(GOVERN_DB)
    expect_raises(
        conn,
        "UPDATE prompt_versions SET prompt_hash=? WHERE id=?",
        ("fakehash", "scout_extraction_v1.0"),
        "content is immutable"
    )
    conn.close()

def test_wizards_seeded_correctly():
    conn = sqlite3.connect(GOVERN_DB)
    rows = conn.execute(
        "SELECT short_name FROM wizards WHERE status='active' ORDER BY short_name"
    ).fetchall()
    names = {r[0] for r in rows}
    expected = {"aria", "marcus", "nova", "sterling", "reina"}
    assert names == expected, f"Expected wizards {expected}, got {names}"
    conn.close()

def test_epoch_seeded_active():
    conn = sqlite3.connect(GOVERN_DB)
    row = conn.execute(
        "SELECT status FROM epochs WHERE id=?", (EPOCH_ID,)
    ).fetchone()
    assert row is not None, "Initial epoch not found"
    assert row[0] == "active", f"Initial epoch should be active, got {row[0]}"
    conn.close()

def test_operator_god_seeded():
    conn = sqlite3.connect(GOVERN_DB)
    row = conn.execute(
        "SELECT role FROM operators WHERE id=?", ("op_god_001",)
    ).fetchone()
    assert row is not None, "God operator not found"
    assert row[0] == "god", f"Operator role should be 'god', got {row[0]}"
    conn.close()

# ============================================================
# CROSS-DOMAIN REFERENCES
# ============================================================

def test_cross_domain_reference_insert():
    conn = sqlite3.connect(KNOWLEDGE_DB)
    atom_id = _insert_test_atom(conn, "Cross domain reference test atom.", "xref1")
    xref_id = "xref_test_001"
    conn.execute("""
        INSERT OR IGNORE INTO cross_domain_references (
            id, source_domain, target_domain, source_atom_id,
            reference_type, noted_by, noted_at
        ) VALUES (?,?,?,?,?,?,?)
    """, (xref_id, "saas_product", "ai_patterns", atom_id,
          "atom_shared", "wiz_nova", NOW))
    conn.commit()
    row = conn.execute(
        "SELECT source_domain, target_domain FROM cross_domain_references WHERE id=?",
        (xref_id,)
    ).fetchone()
    assert row[0] == "saas_product" and row[1] == "ai_patterns", "Cross-domain reference failed"
    conn.close()

# ============================================================
# RUN ALL TESTS
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OHARA — Schema Acceptance Tests")
    print("=" * 60)

    # Vault tests
    print("\n[LAYER 1 — RAW VAULT]")
    test("Insert basic raw_item", test_vault_insert_basic)
    test("Immutability: origin_url blocked", test_vault_immutability_origin_url)
    test("Immutability: content_hash blocked", test_vault_immutability_content_hash)
    test("No DELETE on raw_items", test_vault_no_delete)
    test("Duplicate content_hash rejected", test_vault_duplicate_content_hash)
    test("Status update allowed (mutable field)", test_vault_status_update_allowed)

    # Atom tests
    print("\n[LAYER 2 — ATOMS]")
    test("Insert valid atom", test_atom_insert_basic)
    test("Claim > 280 chars rejected", test_atom_claim_too_long)
    test("Empty source_ids rejected", test_atom_empty_source_ids)
    test("Superseded without pointer rejected", test_atom_superseded_requires_pointer)
    test("Rejected without reason rejected", test_atom_rejected_requires_reason)
    test("No DELETE on atoms", test_atom_no_delete)
    test("Superseded with pointer succeeds", test_atom_superseded_with_pointer)

    # Counter evidence + patterns
    print("\n[LAYER 3 — COUNTER EVIDENCE]")
    test("CE insert updates pattern count", test_counter_evidence_updates_pattern_count)
    test("CE resolution decrements count", test_counter_evidence_resolves_updates_count)
    test("Refuted CE requires rationale", test_ce_refuted_requires_rationale)

    print("\n[LAYER 4 — PATTERNS]")
    test("Structural without human fields rejected", test_pattern_structural_requires_human_fields)
    test("Structural with short rationale rejected", test_pattern_structural_rationale_min_length)
    test("Structural with full fields succeeds", test_pattern_structural_with_full_fields)
    test("No DELETE on patterns", test_pattern_no_delete)
    test("Deprecation without reason rejected", test_pattern_deprecation_requires_reason)

    print("\n[LAYER 5 — BOOKS]")
    test("Pattern deprecation flags stale book dependency", test_book_pattern_dep_staleness_on_deprecation)

    print("\n[EPOCHS]")
    test("Active epoch: model_id frozen", test_epoch_frozen_model_id)
    test("Active epoch: prompt_version frozen", test_epoch_frozen_prompt_version)
    test("Active epoch: scoring_thresholds frozen", test_epoch_frozen_scoring_thresholds)

    print("\n[PROMPT REGISTRY]")
    test("Prompt content immutable after registration", test_prompt_version_immutability)
    test("Prompt hash immutable after registration", test_prompt_version_hash_immutability)

    print("\n[GOVERNANCE SEED]")
    test("All 5 wizards seeded and active", test_wizards_seeded_correctly)
    test("Initial epoch seeded and active", test_epoch_seeded_active)
    test("God operator seeded", test_operator_god_seeded)

    print("\n[CROSS-DOMAIN COLLABORATION]")
    test("Cross-domain reference insert succeeds", test_cross_domain_reference_insert)

    # Results
    total = passed + failed
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} passed")
    print("=" * 60)

    for status, name in results:
        mark = "✓" if status == "PASS" else "✗"
        print(f"  {mark} {name}")

    print("=" * 60)

    if failed > 0:
        print(f"\nPHASE 0 EXIT GATE: BLOCKED — {failed} test(s) failed")
        sys.exit(1)
    else:
        print("\nPHASE 0 EXIT GATE: PASSED — all tests green")
        print("Ready for seed.py and CLI scaffold.")
