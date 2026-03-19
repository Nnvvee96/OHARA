---
system: Atlas Vault OS
version: 3.2
date: March 18, 2026
status: COMMAND_REF / PLAYBOOKS
project: OHARA
dependencies: [[AGENT.md]], [[PATTERNS.md]], [[CONSTRAINTS.md]]
---
# PLAYBOOKS.md - Command & Workflow Reference
# PROJECT: OHARA

# 1. Command Center
Tiered commands; cap at $0.50/task.

| Command | Zweck | Model Tier | Node |
|---------|-------|------------|------|
| /REINDEX | Graph refreshen | Utility | Global |
| /SPECIFY | Architektur locken | Reasoning | TDD.md |
| /SHRED | Plan red-teamen | Reasoning | AUDIT.md |
| /PLAN | Micro-Steps | Balanced | IMPLEMENTATION_PLAN.md |
| /EXECUTE | Implementieren | Balanced | SESSION_LOGS.md |
| /AUDIT | Hardening Gate | Reasoning | AUDIT.md |
| /SKILL | Lektion kodifizieren | Balanced | SKILLS_COMPOUNDING.md |
| /REMEDIATE | Wiederherstellen | Reasoning | RECOVERY_KIT.md |
| /ORCHESTRATE | Wizard-Delegation | Reasoning | AGILE_CYCLES.md |

# 2. Operational Playbooks

Initialization Phase:
  /REINDEX: Scan YAML/Headers aller Atlas-Files.
  Interrogate: Assumptions flaggen.
  /SPECIFY: In TDD.md einfrieren.
  SOUL.md zuerst lesen.

Shred Phase:
  /SHRED: Epistemische Logik und Security brechen.
  Constraint: Kein Execute bis resolved.
  Risk in AUDIT.md definieren.

Action Phase (Wizard-Cycles):
  Loop: Ingest → Extract → Review → Pattern → Book.
  Utility Tier für Tests/Docs.
  God Digest täglich.

Closing Phase:
  /AUDIT: 85% Härtung verifizieren.
  /SKILL: Neue Constraint in SKILLS_COMPOUNDING.md.
  Journal: SESSION_LOGS.md + MEMORY.md updaten.
  Diagnostics: Acceptance Rate + Anomalie-Flags prüfen.

# 3. File Hierarchy (Skill Graph)
YAML required für Scans.

Fundament: SOUL.md (immer zuerst)
Governance: AGENT.md, PATTERNS.md, CONSTRAINTS.md, AUDIT.md, PLAYBOOKS.md
Foundations: SKILLS_COMPOUNDING.md, TECHSTACK.md, RECOVERY_KIT.md
Workflow: CONCEPT.md, IMPLEMENTATION_PLAN.md, TDD.md, MEMORY.md, SESSION_LOGS.md
Zyklen: AGILE_CYCLES.md

# 4. CLI Quick Reference (ohara.py)
ohara.py status — Library-Übersicht
ohara.py ingest --wizard aria --url <url> — URL laden
ohara.py atom create --wizard aria --raw <id> — Atom extrahieren
ohara.py atom list --domain ai_patterns --status candidate — Atoms anzeigen
ohara.py review --wizard aria — Review-Queue
ohara.py pattern create --wizard aria — Pattern erstellen
ohara.py pattern list — Patterns anzeigen
ohara.py god digest — Tägliche Zusammenfassung
ohara.py god approve --pattern <id> — STRUCTURAL Promotion (Gott only)
ohara.py god redirect --wizard <n> --instruction "..." — Wizard anweisen
ohara.py wizards — Wizard-Profile anzeigen

Final Principle: Disziplin über Inspiration.
Halt bei Ambiguität. Keine Annahmen.
SOUL.md hat immer Vorrang.
