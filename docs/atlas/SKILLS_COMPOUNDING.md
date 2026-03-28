---
system: Atlas Vault OS
version: 3.2
date: March 19, 2026
status: STATIC / PERSISTENT
project: OHARA
---
# SKILLS_COMPOUNDING.md - Codified Learnings
# PROJECT: OHARA

## 1. Epistemische Regeln
E#1: Template-Files sofort befüllen. Nie [Insert] stehen lassen.
E#2: utility_vector Pflicht. Kein Atom ohne Nutzvektor.
E#3: SOUL.md hat Vorrang vor Architektur.
E#4: Skeptic-Gate unumgehbar. Keine Ausnahmen.
E#5: Wizard-Personas sind funktional. Schwache Persona = Noise.
E#6: OHARA wird schlauer als sein Schöpfer. Das ist das Ziel.

## 2. Technische Regeln
T#1: SHA Discipline — Epoch-ID auf jedem Atom.
T#2: Append-Only ist nicht verhandelbar.
T#3: Content-Addressed IDs = automatische Dedup.
T#4: Drei Datenbanken, nicht eine.
T#5: Niemals "latest" Model-Alias.
T#6: Secrets nur in .env — niemals in Code oder Chat.
T#7: Bestehende Files updaten, nie duplizieren.
T#8: SSH Key ohne Passwort für automatisierte Scripts (-N "").
T#9: Hetzner Server-Typ: cpx22 (nicht cx11/cx22 — deprecated).
T#10: Reddit 403 auf VPS-IPs — HackerNews RSS als Fallback.

## 3. Operationale Regeln
O#1: Vitality Signals sind die Augen des Systems.
O#2: Wizard-Stille ist ein Signal — 72h = Warning.
O#3: Acceptance Rate 30-60% = gesund.
O#4: King managt Strategie, nicht Taktik.
O#5: Wizard Evolution ist Zivilisations-Mechanik.
O#6: Claude kann kein SSH. Push → user pullt. Webhook löst das später.
O#7: GitHub Token rotieren nach Chat-Sharing. ohara-deploy = permanenter Token.

## 4. Infrastruktur Regeln
I#1: Tailscale zuerst aktivieren bevor SSH-Firewall gesetzt wird.
I#2: deploy.py erkennt bestehenden Server automatisch — kein Doppel-Create.
I#3: Dashboard (Port 7842) Tailscale-only. Nie öffentlich exposen.
I#4: Web Dashboard für tägliche Arbeit. Terminal nur für Setup/Debugging.

## 5. Flush Log
[2026-03-18]: Phase 0 abgeschlossen.
  Größte Lektion: SOUL.md muss vor Architektur dokumentiert sein.
  Duplikate entstehen wenn man nicht prüft was schon existiert.

[2026-03-19]: VPS erfolgreich deployed nach mehreren Fixes:
  - cx11/cx22 deprecated → cpx22
  - SSH Key Passwort Problem → -N "" Flag
  - Server Name Conflict → Script erkennt bestehenden Server
  - Firewall blockiert SSH → Tailscale IP für reconnect
  Lektion: Deploy-Skripte müssen idempotent sein (mehrfach ausführbar).
  Reddit auf VPS blockiert → immer VPS-kompatible Quellen testen.
