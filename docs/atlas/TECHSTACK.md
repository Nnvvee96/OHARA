---
system: Atlas Vault OS
version: 3.2
date: March 18, 2026
status: TEMPLATE / DYNAMIC
project: OHARA
---
# TECHSTACK.md
# PROJECT: OHARA

## 1. Model Routing
Architecture/Reasoning: Gemini 1.5 Pro (kostenlos Phase 1-2)
  Zukunft Phase 3+: claude-opus für Architektur, Skeptic
Worker/Extraktion: Gemini 1.5 Flash (kostenlos, schnell)
  Zukunft Phase 3+: claude-sonnet-4-6 für Extraktion
Swap: LLM_PROVIDER in .env → neue Epoch → nahtlos

Anti-Pattern NEVER:
  - "latest" Alias — immer gepinnte Versionen
  - Model-Wechsel ohne neue Epoch
  - Mehr als $0.50/Task in Phase 1-2

## 2. Harness & Review
Review: ohara.py god digest — täglicher Überblick
Gate: 31 Schema-Tests (tests/schema/test_schema.py)
Evidence: cycle_vitality Records (nicht Screenshots)
Vitality: Acceptance Rate 30-60% = gesund

## 3. Infrastructure & Security
Hosting: Hetzner CX11 (€2.49/mo) — Phase 1-3
  Upgrade CX21 wenn 5+ gleichzeitige Wizards
Location: nbg1 (Nürnberg)
Network: Tailscale — SSH nur via Tailscale IP
  UFW Firewall: DENY all inbound außer Tailscale Port 22
  Password Auth: Deaktiviert
SSH: Ed25519 Key — niemals RSA
Secrets: Nur in .env (gitignored) — NIEMALS in Code oder Chat

Sicherheits-Prinzip (Levels.io):
  Niemand kommt rein außer du via Tailscale.
  Kein öffentlicher Port bis Phase 7 (Library UI).

## 4. Application Stack
Runtime: Python 3.12 + venv
Database: SQLite 3 (WAL mode, foreign_keys=ON)
  ohara_vault.db / ohara_knowledge.db / ohara_governance.db
Content Storage: vault/raw/YYYY/MM/DD/<sha256>.bin
Agent Framework: Custom Python Async Workers (kein Framework)
Scheduling: APScheduler (lokal) → systemd Timer (VPS)
CLI: Click + Rich

Phase 4+ Migration:
  PostgreSQL wenn: 3+ gleichzeitige Wizards / WAL Contention / 500k+ Atome
  Graph DB (Neo4j) als read-only Query Surface für Pattern-Traversal

## 5. Analytics & Growth (Phase 7+)
Tracking: cycle_vitality Tabelle (intern)
Library UI: Next.js (read-only, Phase 7)
Distribution: Wissende selbst (keine externe Distribution in Phase 1-4)

## 6. Locked Versions
Runtime: Python 3.12
Libraries: click, rich, google-generativeai, python-dotenv, requests, paramiko
SQLite: Ubuntu 24.04 System-Version
Node.js: Nicht benötigt bis Phase 7

## 7. Anti-Patterns (NEVER)
NEVER: Model-Version ändern ohne neue Epoch
NEVER: API Keys in Code, Chat, oder Git
NEVER: Raw Vault Items löschen oder überschreiben
NEVER: STRUCTURAL Promotion automatisieren
NEVER: World 2 write-back zu World 1 (außer via Raw Vault Pipeline)
NEVER: DB-Columns umbenennen oder löschen (nur additive Changes)
NEVER: Clawdbot/Hermes für World 1 — das sind World 2 Tools
