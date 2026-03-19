---
system: Atlas Vault OS
version: 1.0
date: March 18, 2026
status: TEMPLATE / DYNAMIC
project: OHARA — The Library of Agentic Wizards
---
# MEMORY.md - Project Knowledge Base
# PROJECT: OHARA

## 1. Strategic Decisions

Decision A: SQLite (3 Datenbanken) > Single DB
  Rationale: Vault/Knowledge/Governance getrennt für unabhängige
  Backup-Policies und klare Grenzen. Migration zu PostgreSQL in Phase 3-4.

Decision B: Custom Python Orchestration > LangGraph/CrewAI/Hermes/Clawdbot
  Rationale: Bestehende Frameworks lösen Execution-Probleme, nicht
  Epistemic-Integrity-Probleme. OHARA ist kein Coding-Agent-System.
  Custom = billiger, auditierbar, owned, epistemisch transparent.

Decision C: Gemini Free Tier (Phase 1-2) > Anthropic API
  Rationale: Kosten. 1500 Requests/Tag kostenlos für Kalibrierung.
  Swap zu Anthropic in Phase 3 wenn Qualität es erfordert.

Decision D: utility_vector als Pflichtfeld auf Atomen
  Rationale: OHARA ist keine Ablage. Atome ohne Nutzvektor werden
  vom Scout automatisch verworfen. SOUL.md Prinzip.

Decision E: STRUCTURAL-Promotion ausschließlich human-only (Gott)
  Rationale: Das höchste Wissen darf nicht automatisiert werden.
  Permanente Regel — keine Ausnahmen, keine Overrides, niemals.

Decision F: Wizard Evolution in Schema von Anfang an angelegt
  Rationale: Phase 6 Wizard Memory/Career/Reproduction Tabellen
  jetzt in governance.sql angelegt damit keine Migration nötig.

## 2. Flush Logs
Compaction: Bei 150k Tokens — destilliere Erkenntnisse hier.

[2026-03-18 Session 1-3]:
  OHARA Phase 0 abgeschlossen. Alle Schemas, 5 Wizards, CLI,
  Scout Agent, Deploy Script gebaut. 31/31 Tests grün.
  Philosophie vollständig in SOUL.md v2.0 dokumentiert.
  utility_vector Schema-Erweiterung implementiert.
  Wizard Evolution Tabellen in governance.sql angelegt.
  Alle 14 Atlas Vault OS Files für OHARA befüllt.

## 3. Locked Prompts
Scout Extraction v1.0: In prompt_versions DB gespeichert.
  Persona-injiziert, utility_vector-bewusst, noise-ablehnend.
Skeptic Adversarial v1.0: In prompt_versions DB gespeichert.
  Aktiv nach Gegenbeweisen suchend, nicht bestätigend.

Visual Seed (Library UI, Phase 7):
  Stimmung: Alte Bibliothek trifft digitale Zivilisation.
  Räume pro Domäne. Bücherregale. Wizard-Statuskarten.
  Pattern-Graphen. Widerspruchs-Maps. Dunkel, warm, lebendig.

## 4. Failure Lessons
Failure: Atlas Vault OS MD-Files nicht sofort für OHARA befüllt.
  Solution: Template-Files immer sofort beim Projektstart befüllen.
  Regel in SKILLS_COMPOUNDING.md dokumentiert.

Failure: Gemini API Key im Chat geteilt.
  Solution: API Keys NUR in secrets.env. Niemals in Chat oder Code.
  Key sofort widerrufen und neu generieren.

Failure: Duplikate in docs/atlas/ erstellt statt Originale zu nutzen.
  Solution: Immer die bestehenden Files nutzen und updaten.
  Niemals Duplikate erstellen.

## 5. Harness Gap Loop
Incident: utility_vector fehlte initial im Atom-Schema.
  New Case: Test — Atom ohne utility_vector wird korrekt verworfen.
  Status: In test_schema.py ergänzen (Phase 1 Aufgabe).
  SLA: Vor Phase 2 Automation gelöst.
