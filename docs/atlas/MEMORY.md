---
system: Atlas Vault OS
version: 3.2
date: March 19, 2026
status: TEMPLATE / DYNAMIC
project: OHARA
---
# MEMORY.md - Project Knowledge Base
# PROJECT: OHARA — The Library of Agentic Wizards

## 1. Strategic Decisions

Decision A: SQLite (3 DBs) > Single DB
  Rationale: Vault/Knowledge/Governance getrennt.
  Migration zu PostgreSQL in Phase 3-4.

Decision B: Custom Python > LangGraph/CrewAI/Hermes/Clawdbot
  Rationale: OHARA ist epistemisch, nicht execution-orientiert.
  Clawdbot/Hermes = World 2 Tools. OHARA = World 1.

Decision C: Gemini Free Tier (Phase 1-2) > Anthropic API
  Rationale: 1500 Requests/Tag kostenlos.
  Swap zu Anthropic wenn Qualität es erfordert.

Decision D: utility_vector als Pflichtfeld
  Werte: product_building, process_improvement, system_enhancement,
  financial, future_optionality, personal_capability,
  creative_enabling, decision_support, self_improvement.

Decision E: STRUCTURAL permanent human-only (King)
  Keine Ausnahmen. Permanent.

Decision F: Wizard-Personas sind funktional
  Persona formt Extraktion. Wizards entwickeln sich über Zeit.

Decision G: Hetzner CPX22 (€8/mo) > andere Anbieter
  Rationale: Beste Preis/Leistung für EU-Nutzer.
  Tailscale für sicheren Zugang. SSH nur via Tailscale.

Decision H: Web Dashboard statt nur CLI
  Flask Dashboard auf Port 7842 (Tailscale-only).
  Ermöglicht Browser-basierte Kontrolle ohne Terminal.

Decision I: Kein Claude Code jetzt (zu teuer für Phase 1)
  Phase 1-2: Gemini kostenlos + manuelles Terminal.
  Phase 3+: Claude Code evaluieren wenn nötig ($20/mo extra).

Decision J: Telegram Bot für mobile Kontrolle (pending)
  Kostenlos. Notifications + einfache Befehle vom Handy.
  Levelsio-Ansatz: Telegram als Bridge zu VPS.

## 2. Flush Logs
[2026-03-18]: Phase 0 abgeschlossen. 31 Tests grün.
  SOUL.md v2.0 vollständig. Alle Atlas-Files befüllt.
  GitHub Repo live.

[2026-03-19]: VPS deployed auf Hetzner CPX22.
  Tailscale aktiv. Dashboard läuft auf Port 7842.
  Problem: Reddit 403 Blocked auf VPS-IPs.
  Lösung pending: HackerNews RSS als primäre Quelle.
  Kosten bestätigt: ~€28/Monat für Phase 1-2.

## 3. Locked Prompts
Scout Extraction: scout_extraction_v1.0
Skeptic Adversarial: skeptic_adversarial_v1.0
Visual Seed (Library UI, Phase 5):
  Dunkel, warm. Alte Bibliothek trifft digitale Zivilisation.
  Fraunces serif + JetBrains Mono. Gold + Teal Akzente.
  Räume pro Domäne. Wizard-Karten. Pattern-Graphen.

## 4. Failure Lessons
Failure: cx11/cx22 Server-Typ deprecated bei Hetzner.
Solution: cpx22 (Regular Performance AMD) verwenden.
  Script erkennt jetzt automatisch verfügbare Typen.

Failure: SSH Key mit Passwort — Paramiko kann nicht verbinden.
Solution: ssh-keygen mit -N "" für Key ohne Passwort.
  Oder ssh-add vor deploy.py.

Failure: Reddit 403 Blocked auf VPS-IPs.
Solution: HackerNews API + RSS Feeds als primäre Quellen.
  Reddit nur von Heimnetzwerk nutzbar.

Failure: GitHub Token im Chat geteilt (2x).
Solution: Token immer als Datei hochladen oder rotieren danach.
  ohara-deploy Token ist der permanente Push-Token.

Failure: Keine automatische Verbindung zwischen Claude und VPS.
Solution: Claude kann kein SSH. Workflow:
  Claude pusht → user macht git pull auf VPS.
  Webhook (pending) wird das automatisieren.

## 5. Harness Gap Loop
Incident: utility_vector fehlte initial.
Resolution: Pflichtfeld implementiert. Scout verwirft ohne UV.
Status: RESOLVED

Incident: Reddit 403 auf VPS.
Resolution: HackerNews RSS als Fallback. Pending deploy.
Status: OPEN — nächste Session

Incident: Kein Auto-Pull auf VPS nach Push.
Resolution: GitHub Webhook + Dashboard Endpoint. Pending.
Status: OPEN — nächste Session

Decision K: Source Adapter Architecture — API/Feed first
  Rationale: Reddit direkt auf VPS = 403 geblockt.
  Lösung: Strukturierte Source Adapters pro Quelle.
  Phase 1: HackerNews API + RSS (kein Auth nötig)
  Phase 2: Reddit API (reddit.com/prefs/apps) + X API (console.x.com)
  Phase 3: Browser-Crawl nur als Fallback
  Regel: API or Feed first. Browser second. Scraping last.
  Referenz: ChatGPT-Recherche März 2026 — Source Adapter Blueprint
