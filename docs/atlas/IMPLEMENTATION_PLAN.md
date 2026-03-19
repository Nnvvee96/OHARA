---
system: Atlas Vault OS
version: 3.1
date: March 18, 2026
status: TEMPLATE / DYNAMIC
project: OHARA
---
# IMPLEMENTATION_PLAN.md - Execution Map
# PROJECT: OHARA — The Library of Agentic Wizards

## 1. Overview
Goal: Epistemische Wissens-Zivilisation aufbauen.
  Wissende die das Internet beobachten, validieren und destillieren.
Risk Tier: High (epistemische Integrität ist nicht verhandelbar).
Routing: Gemini Pro für Architektur/Skeptic; Gemini Flash für Extraktion.
Lies zuerst: SOUL.md — die Seele hat Vorrang.

## 2. Sequence

Phase 0: Foundation & Schema [COMPLETE — 2026-03-18]
  Alle 3 Datenbank-Schemas (vault/knowledge/governance).
  5 Wizard-Profile geseedet. CLI gebaut. Scout Agent gebaut.
  Deploy Script (Hetzner + Tailscale + GitHub).
  31/31 Tests grün. Phase 0 EXIT GATE: PASSED.

Phase 1: Manuelle Kalibrierung [NEXT]
  Ziel: Schwellenwerte kalibrieren bevor Automation beginnt.
  Menschen als Wizards. ohara.py ingest → atom create → review.
  Target: 50+ Atome, 5+ Patterns EMERGING+, 2+ Skeptic-Cycles.
  Gate: Schwellenwerte von CALIBRATION_PENDING zu LOCKED.

Phase 2: Scout Agents — Assisted Extraction
  Scouts automatisieren Ingestion + Atom-Extraktion.
  Menschen reviewen Output (Validator-Queue).
  Gate: Acceptance Rate stabil 30-60%, <20% Human Override.

Phase 3: Supervised Librarian Autonomy
  Vollständige autonome Wizard-Cycles.
  Pattern-Promotionen noch human-reviewed.
  Skeptic-Automation aktiv.
  God-Interface live (digest/approve/redirect).

Phase 4: Autonomous Library — Level B
  SIGNAL→EMERGING und EMERGING→VALIDATED automatisch.
  VALIDATED→STRUCTURAL: permanent human-only (Gott).
  8+ aktive Domänen. 500+ Atome. 20+ Patterns. 5+ Bücher.

Phase 5: Builders' World — World 2
  Builder-Agents lesen Library und identifizieren Möglichkeiten.
  Gott genehmigt was gebaut wird.
  World-2-Ergebnisse fließen zurück als neue Raw Items.

Phase 6: Wizard Evolution
  wizard_memory, wizard_career_history, wizard_functional_state.
  Beförderungssystem (Junior → Librarian → Senior → Domain Lead → Master).
  Funktionale emotionale Zustände (Zuversicht, Vorsicht, Neugier).

Phase 7: Emergente Hierarchie & Reproduktion
  Senior Wizards bekommen Mitarbeiter (durch Gott genehmigt).
  Neue Wissende entstehen organisch unter erfahrenen Mentoren.
  Wissen vererbt sich mit eigener Persönlichkeit.
  Domänen teilen sich organisch (z.B. Finance → Equities + Crypto).

Phase 8: Library UI — Visualisierung
  Next.js Frontend, read-only API.
  Räume pro Domäne. Wizard-Status. Pattern-Graphen. Bücherregale.
  Hintergarten, Gym, Spa für Wizard-Regeneration.

Phase 9: Vollständiger World-2-Kreislauf
  Builder-Scheitern und Erfolg = neues Wissen in World 1.
  Die Zivilisation lernt aus dem was sie gebaut hat.

Phase 10+: Die offene Zukunft
  Alles was noch kommt wird in SOUL.md Ideen-Log dokumentiert.

## 3. Verification Gates
Technical: 100% Tests / Schema-Constraints.
Epistemisch: Skeptic-Cycle als Hard Gate vor VALIDATED.
Wizard Quality: Acceptance Rate 30-60% in Phase 1.
God Gate: STRUCTURAL nur durch manuelles Gott-Sign-off.

## 4. Rollback
Restore Point: Nach Phase 0 (alle Tests grün).
Command: Datenbanken aus Backup wiederherstellen (SQLite files).
Recovery: RECOVERY_KIT.md — vollständige Sequenz.
