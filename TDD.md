---
system: Atlas Vault OS
version: 1.0
date: March 18, 2026
status: TEMPLATE / DYNAMIC
project: OHARA | RISK TIER: High
---
# TDD.md - Technical Design Blueprint
# PROJECT: OHARA

## 1. Harness Contract
Risk Paths: core/db/schema/*.sql, core/scripts/db.py, agents/scouts/scout.py
Checks: 31 Schema-Tests (test_schema.py), Vitality Signals, Epoch-Freeze Triggers
Docs Drift: Schema-Änderungen triggern TDD.md Update + neue Epoch

## 2. Shred
Failure A: Atom ohne utility_vector in Library → Noise-Akkumulation
Failure B: STRUCTURAL Promotion ohne human sign-off → epistemische Korruption
Failure C: Model-Wechsel ohne Epoch → nicht-vergleichbare Atome
Failure D: Raw Vault Mutation → Provenienz-Verlust

## 3. Formal Schemas (Kurzreferenz)
RawItem: id(SHA256), origin_url, domain, epoch_id, content_hash, source_tier
  → Immutable triggers. No UPDATE on content. No DELETE ever.

Atom: id(SHA256 claim+sources+epoch), claim(≤280), claim_type, domain,
  cross_domain_tags, utility_vector, source_ids, source_hash_set,
  epoch_id, model_id, speculation_level(1-5), confidence_score(0-1)
  → No DELETE. Supersede via superseded_by pointer.

Pattern: id(ULID), title(≤120), summary(≤500), status(signal→structural),
  atom_ids[], unresolved_strong_count, structural_approved_by(human only)
  → No DELETE. Deprecate with reason.

CounterEvidence: atom_id → contradicts_pattern_id, severity(weak/moderate/strong/fatal)
  → STRONG/FATAL unresolved blockiert alle Promotions.

Epoch: frozen parameters (prompt_version, model_id, sources, thresholds)
  → Trigger blockiert Updates auf gefrorene Felder.

WizardMemory: (Phase 6) success/failure/insight Logs pro Wizard
WizardCareerHistory: (Phase 6) Beförderungs-Audit-Log
WizardFunctionalState: (Phase 6) confidence/caution/curiosity pro Wizard
WizardReproduction: (Phase 7) Mentor→Junior Beziehungen

## 4. Promotion Rule Contracts
SIGNAL → EMERGING: atoms≥3, independence>0.5, span≥7d, keine FATAL CE
EMERGING → VALIDATED: atoms≥8, independence>0.7, span≥30d, domains≥2,
  confidence_avg>0.65, Skeptic-Cycle PFLICHT, keine STRONG/FATAL CE
VALIDATED → STRUCTURAL: span≥90d, human sign-off PFLICHT,
  rationale≥100 chars, adversarial audit abgeschlossen

## 5. Quality Gates
- SHA-Match: Atom-ID muss reproduzierbar sein (gleiche Inputs = gleiche ID)
- Epoch Gate: Atome ohne gültige Epoch werden abgelehnt
- Utility Gate: Atome ohne utility_vector werden verworfen
- Skeptic Gate: EMERGING→VALIDATED blockiert ohne completed skeptic_cycle
- Structural Gate: DB CHECK constraint enforced — kein Bypass möglich
- Vitality Gate: Cycle ohne Vitality Record = FAILED

## 6. Acceptance Tests
31 Tests in tests/schema/test_schema.py — alle müssen grün sein.
Phase 0 Exit Gate: PASSED [2026-03-18]
