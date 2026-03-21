---
system: Atlas Vault OS
version: 3.2
date: March 19, 2026
status: ACTIVE / DYNAMIC
project: OHARA
---
# TECHSTACK.md
# PROJECT: OHARA

## 1. Model Routing
Extraktion (Scout): gemini-1.5-flash (kostenlos Phase 1-2)
Reasoning (Skeptic): gemini-1.5-pro (kostenlos Phase 1-2)
Phase 3+: claude-sonnet-4-6 wenn Qualität es erfordert
Swap: LLM_PROVIDER in .env → neue Epoch → nahtlos

Anti-Pattern: Niemals "latest" Alias. Niemals Model-Wechsel ohne Epoch.
Kosten: ~€28/Monat total für Phase 1-2 (VPS + Claude.ai Pro)

## 2. Infrastruktur (LIVE)
VPS: Hetzner CPX22, nbg1, Ubuntu 24.04
  Public IP: 178.104.84.117
  Tailscale IP: 100.118.247.94
  Preis: ~€8/Monat
  Pfad: /opt/ohara
  Services: ohara-scouts.timer, ohara-dashboard

Sicherheit:
  SSH: Ed25519 Key (~/.ssh/id_ohara) ohne Passwort
  Firewall: UFW, deny all inbound außer Tailscale
  Tailscale: Beide Geräte verbunden (MacBook + VPS)
  Port 7842: Tailscale-only (Dashboard)

SSH Zugang:
  ssh root@100.118.247.94

Update nach Push:
  ssh root@100.118.247.94 'cd /opt/ohara && git pull && systemctl restart ohara-scouts.timer ohara-dashboard'

## 3. Datenbank
SQLite (3 Dateien auf VPS: /opt/ohara/core/db/)
  ohara_vault.db / ohara_knowledge.db / ohara_governance.db
WAL mode, foreign_keys=ON

Phase 4+: PostgreSQL wenn 3+ gleichzeitige Wizards

## 4. Source Access
Phase 1 (aktuell — problem bekannt):
  Reddit API: 403 BLOCKED auf VPS-IPs → FIX PENDING
  HackerNews RSS: hnrss.org/frontpage → FUNKTIONIERT
  Fix: Wizard signal_sources auf HackerNews umstellen

Phase 2+:
  HackerNews API (firebase, kein Auth)
  RSS Feeds (öffentliche Blogs, Substack)
  Reddit: nur wenn Proxy/residential IP verfügbar

## 5. Web Dashboard
URL: http://100.118.247.94:7842 (Tailscale-only)
Tech: Flask + vanilla HTML/CSS/JS
Features: Stats, Review Queue, Scout Trigger, Logs
Service: ohara-dashboard.service (systemd)

## 6. Versionskontrolle
Repo: github.com/Nnvvee96/OHARA (privat)
Branch: main
Push-Token: ohara-deploy (in secrets.env)
Auto-Push: via Claude in diesem Chat
Auto-Pull: Pending (GitHub Webhook)

## 7. Pending Installs
[ ] Telegram Bot (python-telegram-bot, kostenlos)
[ ] GitHub Webhook → Auto-Pull auf VPS
[ ] HackerNews als primäre Scout-Quelle deployen
[ ] Claude Code (Phase 3+, $20/mo extra, optional)

## 8. Anti-Patterns (NEVER)
NEVER: Model-Version ändern ohne neue Epoch
NEVER: API Keys in Code, Chat oder Git
NEVER: Raw Vault Items löschen
NEVER: STRUCTURAL Promotion automatisieren
NEVER: cx11/cx22 als Hetzner Server-Typ (deprecated)
NEVER: SSH Key mit Passwort für automatisierte Scripts
NEVER: Reddit als primäre VPS-Quelle (403 blocked)

## 9. Source Adapter Architecture (LOCKED)

Prinzip: API or Feed first. Browser second. Scraping last.
Nie "das Internet durchforsten" als einzigen Mechanismus.

OHARA hat Source Adapters — pro Quelle ein definierter Adapter:

PHASE 1 (jetzt — stabil, kostenlos):
  HackerNews Adapter → offizielle Firebase API (kein Auth)
  RSS Adapter → öffentliche Feeds (Blogs, Substack, GitHub Releases)

PHASE 2 (Reddit + X):
  Reddit Adapter → API (reddit.com/prefs/apps → client_id/secret)
    Config: Subreddits pro Wizard, min_score, max_age_hours
    Polling: alle 3h pro Subreddit
  X Adapter → offizielle API (console.x.com)
    Pfad A: eigene Bookmarks (high-signal, manuell gefiltert)
    Pfad B: thematische Suche + Listen (autonome Discovery)

PHASE 3 (Fallback):
  Browser-Crawl → nur für Quellen ohne API/RSS
    Streng rate-limited. Niemals als Standardpfad.

Pro Wizard YAML-Config:
  sources:
    reddit:
      subreddits: [programming, webdev, SaaS, MachineLearning]
      min_score: 5
      max_age_hours: 24
    x:
      modes: [bookmarks, search]
      queries: ['"AI agents" AND "SaaS"', '"vibe coding"']
    rss:
      feeds: [hnrss.org/frontpage, hnrss.org/newest?points=50]

Anti-Pattern NEVER:
  NEVER: Reddit direkt ohne API (403 auf VPS-IPs)
  NEVER: Browser-Scraping als primäre Quelle
  NEVER: Quellen ohne definierte Adapter
