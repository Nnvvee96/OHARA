---
system: Atlas Vault OS
version: 3.1
date: March 18, 2026
status: GOVERNANCE / CONSTRAINTS
project: OHARA
dependencies: [[PATTERNS.md]], [[AGENT.md]], [[AUDIT.md]]
---
# CONSTRAINTS.md - Core Operating Constraints
# PROJECT: OHARA

# 1. Strategic Constitution

Wissen vs. Information
  OHARA akkumuliert Wissen, nicht Information.
  Filter: Steckt da etwas Strukturelles das jetzt, später oder in der
  Zukunft irgendeinen Wert hat — für Geld, Prozesse, Produkte,
  Fähigkeiten, Kreativität, Entscheidungen, oder die Wissenden selbst?

85% Hardening Rule
  Kein Pattern ist Done bis 85% gehärtet.
  Härtung = Skeptic-Cycle + Counter-Evidence reviewed + Zeitpersistenz.

Spec-Driven Epistemik
  Neue Domänen erst aktivieren wenn Persona, Signal-Perimeter und
  Kalibrierungsziele definiert sind.

# 2. Economic & Context Constraints

Model Arbitrage
  Flash für Extraktion (hoch-volume, kostenlos Phase 1-2).
  Pro für Reasoning/Skeptic (kostenlos Phase 1-2).
  Cap: Kosten pro akzeptiertem Atom tracken.

Context Traversal
  SOUL.md zuerst. Dann AGENT.md. Dann relevante Files.
  Selective loading — nie alles auf einmal.

# 3. Quality & Evidence Constraints

Utility Vector Pflicht
  Atome ohne utility_vector werden verworfen.
  OHARA ist keine Ablage — es ist eine Schatzkammer.

Harness Risk Tiers
  High-Risk (STRUCTURAL): Manuelles King-Sign-off + vollständige Dokumentation.
  Low-Risk (SIGNAL→EMERGING): Automatisierte Regelprüfung erlaubt.

Evidence over Claims
  Atome brauchen Quellen-IDs. Patterns brauchen Atom-IDs.
  Menschliche Behauptungen ohne Quellen werden abgelehnt.

# 4. Zivilisations-Constraints

Organisches Wachstum
  Wizard-Roster wächst nur durch Gap-Detection.
  Wizard-Reproduktion nur durch King-Genehmigung nach Verdienst-Nachweis.

Wizard-Autonomie-Grenzen
  Wizards schlagen vor. Regeln entscheiden (bis VALIDATED).
  King entscheidet (ab STRUCTURAL).
  Verboten für Wizards: direkt STRUCTURAL promoten,
  Raw Vault modifizieren, domänenfremd schreiben ohne cross_domain_tags.

World-2-Firewall
  World 2: read-only Zugriff auf World 1.
  Kein Write-back außer via Raw-Vault-Eingang (neue Rohdaten).

Keine Duplikate
  Immer prüfen ob ein File/Schema/Concept bereits existiert.
  Update statt neuerstellen.

# 5. Final Operating Principle
SOUL.md ist das Fundament. Alle Constraints dienen der Seele.
Wenn ein Constraint die Vision von OHARA als lebende Wissens-Zivilisation
behindert: Constraint überdenken, Vision bewahren.
