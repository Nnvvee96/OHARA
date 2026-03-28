---
system: Atlas Vault OS
version: 3.2
date: March 19, 2026
status: ACTIVE / DYNAMIC
project: OHARA
---
# IMPLEMENTATION_PLAN.md - Execution Map
# PROJECT: OHARA — The Library of Agentic Wizards

## 1. Overview
Goal: Epistemische Wissens-Zivilisation — Library of Agentic Wizards.
Risk Tier: High (epistemische Integrität nicht verhandelbar).
Lies zuerst: SOUL.md — Seele hat Vorrang.

## 2. Sequence

Phase 0: Foundation & Schema [COMPLETE — 2026-03-18]
  ✓ 3 Datenbank-Schemas (vault/knowledge/governance)
  ✓ 5 Wizard-Profile (Aria, Marcus, Nova, Sterling, Reina)
  ✓ CLI gebaut (ohara.py)
  ✓ Scout Agent (Gemini-powered, utility_vector-aware)
  ✓ Deploy Script (Hetzner + Tailscale + GitHub)
  ✓ 31/31 Tests grün
  ✓ GitHub Repo live (Nnvvee96/OHARA)
  EXIT GATE: PASSED

VPS Deploy [COMPLETE — 2026-03-19]
  ✓ Hetzner CPX22 provisioniert (178.104.84.117)
  ✓ Tailscale aktiv (100.118.247.94)
  ✓ OHARA läuft 24/7
  ✓ Web Dashboard: http://100.118.247.94:7842
  ✓ Systemd Services aktiv

Pending (vor Phase 1):
  [ ] Scout-Quellen fixen (Reddit → HackerNews)
  [ ] GitHub Webhook (Auto-Pull)
  [ ] Telegram Bot (mobile Kontrolle)

Phase 1: Manuelle Kalibrierung [NEXT — ~4 Wochen]
  Schwellenwerte sind CALIBRATION_PENDING.
  Humans als Wizards — manuelle Atom-Extraktion.
  Ziele:
    50+ Atome (3+ Domänen)
    5+ Patterns EMERGING+
    2+ Skeptic-Cycles
    Acceptance Rate 30-60% kalibriert
  Tools: ohara.py ingest / atom create / review / pattern
  EXIT GATE: Thresholds CALIBRATION_PENDING → LOCKED

Phase 2: Scout Automation [~4 Wochen nach Phase 1]
  Scouts laufen automatisch stündlich.
  HackerNews, RSS, öffentliche Feeds.
  Review-Queue täglich (10-15 Min).
  EXIT GATE: Acceptance Rate stabil, <20% Human Override

Phase 3: Volle Wizard-Autonomie [~6 Wochen]
  SIGNAL→VALIDATED automatisch.
  Skeptic-Cycles automatisch.
  King Digest: 5-10 Min täglich.
  STRUCTURAL: permanent nur King.

Phase 4: Autonome Library [Ongoing]
  8+ aktive Domänen.
  500+ Atome, 20+ Patterns, 5+ Bücher.
  EXIT GATE für Phase 5: 3+ Monate stabil

Phase 5: Library UI & Wizard Dashboard
  Next.js Frontend, read-only API.
  Wizard erstellen per UI.
  Bücherregale, Pattern-Graph, Atom-Explorer.
  King-Dashboard mit STRUCTURAL Queue.

Phase 6: Builders' World (World 2)
  Builder-Agents lesen Library.
  Vorschläge → King genehmigt → Builder bauen.
  Clawdbot/Hermes/Paperclip als World-2-Tools.
  Ergebnisse fließen zurück in World 1.

Phase 7: Wizard Evolution & Reproduktion
  wizard_memory, wizard_career_history.
  Beförderungssystem (Junior→Senior→Master).
  Seniors bekommen Mitarbeiter (King genehmigt).
  Domänen teilen sich organisch.

Phase 8: Räume der Zivilisation
  Hintergarten (Reflexion), Gym (Training), Spa (Regeneration).
  Konferenzraum (Wizard-Meetings).
  Wenn kognitive KI-Fähigkeiten es ermöglichen.

Phase 9: Vollständiger World-2-Kreislauf
  Builder-Scheitern/-Erfolg → neue Raw Items in World 1.
  OHARA lernt aus dem was es gebaut hat.

Phase 10+: Die offene Zukunft
  OHARA wird schlauer als sein Schöpfer.
  Alle neuen Ideen → SOUL.md Ideen-Log → hier eingetragen.

## 3. Verification Gates
Technical: 31/31 Tests, Schema-Constraints.
Epistemic: Skeptic-Cycle als Hard Gate vor VALIDATED.
Wizard Quality: Acceptance Rate 30-60%.
God Gate: STRUCTURAL nur durch manuelles Sign-off.

## 4. Rollback
Restore: git pull auf VPS + DB aus Backup.
Backup: /opt/ohara/core/db/*.db täglich sichern.
Recovery: RECOVERY_KIT.md vollständige Sequenz.
