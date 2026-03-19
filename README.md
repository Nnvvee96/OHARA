# OHARA — The Library of Agentic Wizards
## Master Document Index

---

## ZUERST LESEN
docs/SOUL.md — Die Seele. Die Philosophie. Das Fundament.
  Lesen vor allem anderen. Immer.

---

## Strategische Dokumente
docs/concept.md          — Was OHARA ist und was gebaut wird
docs/implementation_plan.md — Wie es gebaut wird (Phase 0-10+)
docs/tdd.md              — Technische Spezifikationen & Schemas

---

## Atlas Vault OS (Governance & Orchestration)
docs/atlas/AGENT.md           — Operator-Identität & Governance-Logik
docs/atlas/CONCEPT.md         — Strategischer Blueprint (OHARA-spezifisch)
docs/atlas/MEMORY.md          — Projekt-Wissensbasis & Entscheidungs-Log
docs/atlas/SESSION_LOGS.md    — Echtzeit-Zustand & Checkpoints
docs/atlas/TECHSTACK.md       — Technologie-Entscheidungen & Anti-Patterns
docs/atlas/SKILLS_COMPOUNDING.md — Kodifizierte Lernpunkte
docs/atlas/RECOVERY_KIT.md    — Wiederherstellungs-Guide
docs/atlas/AUDIT.md           — Architektur-Audits & Red-Team Findings
docs/atlas/CONSTRAINTS.md     — Kern-Betriebsregeln
docs/atlas/PLAYBOOKS.md       — Befehlsreferenz & Workflows
docs/atlas/PATTERNS.md        — Wiederverwendbare Prinzipien
docs/atlas/AGILE_CYCLES.md    — Adaptive Orchestrierungs-Zyklen

---

## Technische Dokumente
core/db/schema/vault.sql      — Raw Item Schema (unveränderlich)
core/db/schema/knowledge.sql  — Atom/Pattern/Book Schemas
core/db/schema/governance.sql — Epoch/Wizard/Vitality Schemas

---

## Betrieb
docs/QUICKSTART.md            — Phase 1 Schnellstart
secrets.example               — API Key Template (kopieren zu secrets.env)
deploy.py                     — Ein-Befehl VPS Deploy

---

## Daten (nicht in Git)
core/db/*.db                  — SQLite Datenbanken (auf VPS)
core/vault/raw/               — Raw Content Files (auf VPS)
.env / secrets.env            — API Keys (NIEMALS in Git)

---

## Philosophie in einem Satz
OHARA ist eine lebende Zivilisation aus Wissenden die aus dem Internet
destilliert was wirklich wichtig ist — und irgendwann mehr weiß als ihr Schöpfer.
