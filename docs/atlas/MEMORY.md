---
system: Atlas Vault OS
version: 3.2
date: March 18, 2026
status: TEMPLATE / DYNAMIC
project: OHARA
---
# MEMORY.md - Project Knowledge Base
# PROJECT: OHARA — The Library of Agentic Wizards

## 1. Strategic Decisions
Decision A: SQLite (3 DBs) > Single DB
  Rationale: Vault/Knowledge/Governance getrennt für unabhängige Backup-Policies.
  Migration zu PostgreSQL in Phase 3-4.

Decision B: Custom Python Orchestration > LangGraph/CrewAI/Hermes/Clawdbot
  Rationale: OHARA ist kein Coding-Agent-System. Es ist ein epistemisches System.
  Bestehende Frameworks lösen Execution-Probleme, nicht Epistemic-Integrity.
  Clawdbot/Hermes = World 2 Tools. OHARA = World 1. Verschiedene Kategorien.

Decision C: Gemini Free Tier (Phase 1-2) > Anthropic API
  Rationale: Kosten. 1500 Requests/Tag kostenlos für Kalibrierung.
  Swap zu Anthropic wenn Qualität es erfordert (neue Epoch).

Decision D: utility_vector als Pflichtfeld auf Atomen
  Rationale: OHARA ist keine Ablage. Atome ohne Nutzvektor = Noise.
  Werte: product_building, process_improvement, system_enhancement,
  financial, future_optionality, personal_capability, creative_enabling,
  decision_support, self_improvement (für Wissende selbst).

Decision E: STRUCTURAL-Promotion ausschließlich human-only (Gott)
  Rationale: Das höchste Wissen darf nicht automatisiert werden. Permanent.

Decision F: Wizard-Personas sind funktional, nicht dekorativ
  Rationale: Persona formt Extraktion und Bewertung. Schwache Persona = Noise.
  Wizards entwickeln sich wie echte Menschen über Zeit.

## 2. Flush Logs
Compaction: Bei 150k Tokens — distilliere Erkenntnisse hier.
[2026-03-18]: Phase 0 abgeschlossen. 31/31 Tests grün. 5 Wizards aktiv.
  CLI, Scout Agent, Deploy Script gebaut. SOUL.md v2.0 vollständig.
  Philosophie: Zivilisation aus Wissenden, Wizard Evolution, Reproduktion,
  Räume (Hintergarten/Gym/Spa), World-2-Kreislauf, OHARA wird schlauer
  als sein Schöpfer. Alle Atlas Vault OS Files für OHARA befüllt.

## 3. Locked Prompts
Scout Extraction: scout_extraction_v1.0 (in prompt_versions DB)
  Persona-injiziert, utility_vector-bewusst, noise-ablehnend.
Skeptic Adversarial: skeptic_adversarial_v1.0 (in prompt_versions DB)
  Aktiv nach Gegenbeweisen suchend — niemals bestätigend.
Visual Seed (Library UI, Phase 7):
  Stimmung: Alte Bibliothek trifft digitale Zivilisation.
  Räume pro Domäne. Wizard-Statuskarten. Pattern-Graphen. Dunkel, warm, lebendig.

## 4. Failure Lessons
Failure: Atlas Vault OS MD-Files nicht sofort für OHARA befüllt.
Solution: Template-Files sind beim Projektstart sofort zu befüllen.
  Regel → SKILLS_COMPOUNDING.md E#1.

Failure: Neue Files erstellt statt bestehende zu nutzen → Duplikate.
Solution: Immer zuerst prüfen ob ein bestehendes File existiert.
  Bestehende Files updaten, nie duplizieren.

Failure: Gemini API Key im Chat geteilt.
Solution: API Keys NUR in secrets.env. Sofort widerrufen wenn im Chat.

## 5. Harness Gap Loop
Incident: utility_vector fehlte initial im Atom-Schema.
Issue: Atome ohne Nutzvektor bringen Noise in die Library.
New Case: Test — Atom ohne utility_vector wird korrekt vom Scout verworfen.
Status: In test_schema.py ergänzen (Phase 1 Aufgabe).
SLA: Vor Phase 2 Automation gelöst.
