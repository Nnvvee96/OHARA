---
system: Atlas Vault OS
version: 3.2
date: March 18, 2026
status: STATIC / PERSISTENT
project: OHARA
---
# SKILLS_COMPOUNDING.md - Codified Learnings
# PROJECT: OHARA

## 1. Epistemische Regeln
E#1: Template-Files sofort beim Projektstart befüllen.
  Platzhalter [Insert] sind technische Schulden. Sofort eliminieren.

E#2: utility_vector ist Pflicht auf jedem Atom.
  Atome ohne Nutzvektor werden verworfen. OHARA ist Schatzkammer, kein Archiv.
  Werte: product_building, process_improvement, system_enhancement,
  financial, future_optionality, personal_capability, creative_enabling,
  decision_support, self_improvement.

E#3: SOUL.md hat Vorrang vor Architektur.
  Bei Konflikt: Technische Entscheidung überdenken, nicht SOUL.md.

E#4: Skeptic-Cycle ist unumgehbar.
  EMERGING → VALIDATED ohne Skeptic = epistemische Korruption.

E#5: Wizard-Personas sind funktional, nicht dekorativ.
  Schwache Persona = schwache Extraktion = Noise in der Library.
  Personas wachsen über Zeit — das ist das Design.

E#6: OHARA wird schlauer als sein Schöpfer.
  Das ist das Ziel. Die Wissenden akkumulieren domänenspezifisches
  Wissen das den Gott in seinen Entscheidungen übersteigt.

## 2. Technische Regeln
T#1: SHA Discipline — Epoch-ID auf jedem Atom.
  Atome ohne Epoch sind nicht vergleichbar.

T#2: Append-Only ist nicht verhandelbar.
  Raw Vault niemals updaten/löschen.
  Atoms: superseded_by statt Delete.
  Patterns: deprecated mit Grund statt Delete.

T#3: Content-Addressed IDs für unveränderliche Objekte.
  Gleicher Content + gleiche Quellen + gleiche Epoch = gleiche ID = Dedup.

T#4: Drei Datenbanken, nicht eine.
  vault / knowledge / governance getrennt. Klare Grenzen.

T#5: Niemals "latest" Model-Alias.
  Immer gepinnte Versionen. Model-Wechsel = neue Epoch.

T#6: Secrets nur in .env — niemals in Code oder Chat.
  Im Chat geteilt = sofort widerrufen, neu generieren.

T#7: Bestehende Files updaten, nie duplizieren.
  Vor dem Erstellen immer prüfen ob File bereits existiert.

## 3. Operationale Regeln
O#1: Vitality Signals sind die Augen des Systems.
  Kein Record = Cycle gilt als FAILED.

O#2: Wizard-Stille ist ein Signal.
  72h kein Cycle = Warning. 120h = Critical. Infrastruktur prüfen.

O#3: Acceptance Rate ist der Qualitätsindikator.
  Ziel Phase 1: 30-60%.
  <20% = Prompt-Problem. >80% = Filter zu locker.

O#4: Gott managt Strategie, nicht Taktik.
  STRUCTURAL Promotions: deine Aufgabe.
  Einzelne Atome: nicht deine Aufgabe.

O#5: Wizard Evolution ist Zivilisations-Mechanik.
  Beförderung durch Verdienst. Reproduktion durch Verdienst.
  Nie vorab planen — organisch entstehen lassen.

## 4. Flush Log
[2026-03-18]: Phase 0 abgeschlossen. Größte Lektion:
  Philosophie (SOUL.md) muss vor Architektur dokumentiert sein.
  Duplikate entstehen wenn man nicht zuerst prüft was schon existiert.
  Wizard-Personas und Wizard-Evolution sind keine Features — sie sind
  der Kern der Zivilisations-Mechanik die OHARA von anderen Systemen unterscheidet.
