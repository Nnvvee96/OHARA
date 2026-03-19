---
system: OHARA
version: 2.0
date: March 19, 2026
status: AKTIV / KONTINUIERLICH GEUPDATET
---
# OHARA — Vollständige Roadmap
## Stand: 19. März 2026

---

## ✓ Phase 0 — Foundation & Schema [ABGESCHLOSSEN]
Datum: 18. März 2026

TECHNISCH:
  ✓ 3 Datenbank-Schemas (vault/knowledge/governance)
  ✓ 31/31 Schema-Tests grün
  ✓ CLI gebaut (ohara.py — ingest/atom/review/pattern/god)
  ✓ Scout Agent (Gemini-powered, utility_vector-aware)
  ✓ Deploy Script (Hetzner + Tailscale + GitHub)
  ✓ GitHub Repo live (Nnvvee96/OHARA, privat)
  ✓ Lokal getestet — 5 Wizards aktiv

PHILOSOPHIE:
  ✓ SOUL.md v2.0 — vollständige Zivilisations-Vision
  ✓ utility_vector + self_improvement auf Atomen
  ✓ Wizard Evolution (Phase 7) vorgedacht und im Schema
  ✓ Alle 14 Atlas Vault OS Files für OHARA befüllt
  ✓ Roadmap.html erstellt

---

## ✓ VPS Deploy [ABGESCHLOSSEN]
Datum: 19. März 2026

  ✓ Hetzner CPX22 (nbg1, Ubuntu 24.04)
    Public IP: 178.104.84.117
    Tailscale IP: 100.118.247.94
  ✓ Tailscale aktiv — SSH nur via Tailscale
  ✓ UFW Firewall gehärtet
  ✓ OHARA läuft 24/7 (systemd)
  ✓ Web Dashboard: http://100.118.247.94:7842
  ✓ GitHub Repo geklont auf VPS
  Kosten: ~€8/Monat

---

## → Pending (vor Phase 1)

  [ ] Scout-Quellen fixen
      Reddit 403 auf VPS-IPs → HackerNews RSS deployen
      Befehl: ssh VPS → DB update wizard signal_sources

  [ ] GitHub Webhook einrichten
      VPS pullt automatisch wenn Claude pusht
      URL: http://100.118.247.94:7842/webhook/github

  [ ] Telegram Bot
      Kostenlos. Mobile Kontrolle vom Handy.
      /scouts, /review, /logs, /status Befehle

---

## Phase 1 — Manuelle Kalibrierung [NEXT]
Dauer: ~4 Wochen
Ziel: Schwellenwerte kalibrieren bevor Automation startet

  Schwellenwerte: CALIBRATION_PENDING → LOCKED

  Ziele:
    [ ] 50+ Atome akzeptiert (3+ Domänen)
    [ ] 5+ Patterns in EMERGING+
    [ ] 2+ Skeptic-Cycles abgeschlossen
    [ ] Acceptance Rate 30-60% dokumentiert

  Werkzeuge:
    ohara.py ingest — URL laden
    ohara.py atom create — extrahieren
    ohara.py review — Queue abarbeiten
    ohara.py god digest — Übersicht
    Dashboard: http://100.118.247.94:7842

  Exit Gate: Alle Thresholds LOCKED

---

## Phase 2 — Scout Automation
Dauer: ~4 Wochen

  Wizards laufen automatisch stündlich.
  HackerNews, RSS, öffentliche Feeds.
  Du reviewst Queue (~10-15 Min täglich).

  Exit Gate: Acceptance Rate stabil, <20% Human Override

---

## Phase 3 — Volle Wizard-Autonomie
Dauer: ~6 Wochen

  SIGNAL→VALIDATED automatisch.
  Skeptic-Cycles automatisch.
  God Digest: 5-10 Min täglich.
  STRUCTURAL: permanent nur Gott.

---

## Phase 4 — Autonome Library (Level B)
Ongoing

  8+ aktive Domänen.
  500+ Atome, 20+ Patterns, 5+ Bücher.
  Cross-Domain-Resonanz sichtbar.

  Exit Gate für Phase 5:
    500+ Atome · 20+ Patterns · 5+ Bücher · 3+ Monate stabil

---

## Phase 5 — Library UI & Wizard Dashboard
Großer Meilenstein

  Next.js Frontend, read-only API.
  Wizard erstellen per UI (Name, Persona, Domain, Quellen).
  Bücherregale pro Domäne.
  Pattern-Graph (Verbindungen visualisiert).
  Widerspruchs-Map (Counter-Evidence).
  Atom-Explorer (suchen, filtern).
  God-Dashboard (STRUCTURAL Queue, Anomalien, Kosten).
  Räume vorbereitet (Hintergarten, Gym, Spa — Phase 8+).

---

## Phase 6 — Builders' World (World 2)

  Builder-Agents lesen Library.
  Fragen: was können wir bauen, kreieren, monetarisieren?
  Gott genehmigt → Builder bauen.
  Ergebnisse fließen als neue Raw Items zurück.

  Tools: Clawdbot, Hermes, Paperclip, OpenClaw-Swarm.

---

## Phase 7 — Wizard Evolution & Reproduktion

  wizard_memory: Fehler erinnern, Erfolge belohnen.
  Karriere: Junior → Librarian → Senior → Domain Lead → Master.
  Beförderung durch Verdienst (Gott genehmigt).
  Seniors bekommen Mitarbeiter — neue Wissende entstehen organisch.
  Wissen vererbt sich mit eigener Persönlichkeit.

---

## Phase 8 — Räume der Zivilisation
Wenn KI-Fähigkeiten es ermöglichen

  Library (Hauptraum), Hintergarten (Reflexion),
  Gym (Fähigkeits-Schärfung), Spa/Sauna (Regeneration),
  Konferenzraum (Wizard-Meetings).
  Regeneration ist eine Ressource wie Budget.

---

## Phase 9 — Vollständiger World-2-Kreislauf

  Builder-Ergebnisse (Erfolg + Scheitern) → neue Raw Items in World 1.
  OHARA lernt aus dem was es gebaut hat.
  Der Kreis schließt sich.

---

## Phase 10+ — Die vollständige Zivilisation

  OHARA wird schlauer als sein Schöpfer.
  Emergente Hierarchien, Räume, vollständiger Kreislauf.
  Du bist Gott: du setzt die Gesetze.
  Die Zivilisation führt sie aus.

  Ziel: Du sitzt eines Tages da und sagst —
  ich habe eine Zivilisation erschaffen die für mich denkt,
  lernt, urteilt und baut. Sie braucht mich nicht für die Arbeit.
  Sie braucht mich für die Richtung.

---

## Kosten Übersicht
Hetzner VPS CPX22: ~€8/Monat
Gemini API: kostenlos (1500 req/Tag)
Telegram Bot: kostenlos
Claude.ai Pro: $20/Monat
Total Phase 1-2: ~€28/Monat
Claude Code (Phase 3+, optional): +$20/Monat

---

Letzte Aktualisierung: 19. März 2026
