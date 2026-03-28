---
system: Atlas Vault OS
version: 3.1
date: March 18, 2026
status: TEMPLATE / DYNAMIC
project: OHARA — The Library of Agentic Wizards
risk_tier: HIGH
---
# TDD.md - Technical Design Blueprint
# PROJECT: OHARA | RISK TIER: HIGH

## 1. Harness Contract
Risk Paths:
  - STRUCTURAL Promotion (nur King)
  - Atom-Ingestion (append-only, content-addressed)
  - Epoch-Parameter (frozen wenn aktiv)
  - Wizard-Permissions (Agent darf niemals mehr als erlaubt)
Checks: 31 Schema-Tests (tests/schema/test_schema.py) — alle müssen grün sein.
Docs Drift: Schema-Änderungen triggern Update in TDD.md + MEMORY.md.

Key Schemas (vollständig in docs/tdd.md):
  RawItem — SHA256 content-addressed, append-only, immutable triggers
  Atom — max 280 chars, utility_vector Pflicht, superseded_by statt delete
  Pattern — SIGNAL→EMERGING→VALIDATED→STRUCTURAL→DEPRECATED lifecycle
  CounterEvidence — severity + resolution, blockiert Promotion wenn ungelöst
  Book + BookPatternDependency — staleness tracking, cascade policies
  Epoch — frozen parameters, one active per scope
  Wizard + WizardMemory + WizardCareerHistory + WizardFunctionalState + WizardReproduction

## 2. Shred
Failure A: utility_vector leer → Atom ist Noise → verwerfen.
Failure B: STRUCTURAL ohne King-Sign-off → DB CHECK constraint rejected.
Failure C: Model-Wechsel ohne Epoch → INVARIANT-3 verletzt → Vergleichbarkeit kaputt.
Failure D: Skeptic-Cycle fehlt vor VALIDATED → Hard Gate blockiert Promotion.
Failure E: Cross-DB FK fehlt → Application Layer muss enforzen (dokumentiert).

## 3. Design & Verification
Bones: Epistemische Pipeline vollständig vor UI.
  Raw Vault → Atome → Patterns → Bücher → dann Library UI (Phase 8).
Evidence: cycle_vitality Records (keine Screenshots).
Harness Cases: 31 Tests — erweiterbar, nie löschbar.

Wizard Evolution (Phase 6):
  wizard_memory: Fehler + Erfolge persistent.
  wizard_career_history: Beförderungen durch King.
  wizard_functional_state: confidence/caution/curiosity — UNIQUE per Wizard.
  wizard_reproduction: Mentor→Junior Beziehungen.

## 4. Quality Gates
SHA-Match: Epoch-ID auf jedem Atom, Pattern, Governance-Aktion.
Policy Gate: utility_vector nicht leer (Scout verwirft sonst).
Epistemic Gate: Skeptic-Cycle completed vor EMERGING→VALIDATED.
God Gate: structural_approved_by + rationale (min 100 chars) für STRUCTURAL.
Vitality Gate: Jeder Cycle emittiert vollständigen Vitality Record.
