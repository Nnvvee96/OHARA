---
system: Atlas Vault OS
version: 1.0
date: March 18, 2026
status: TEMPLATE / DYNAMIC
project: OHARA
---
# TECHSTACK.md
# PROJECT: OHARA

## 1. Model Routing
Extraktion (Scout): gemini-1.5-flash (kostenlos, Phase 1-2)
Reasoning (Skeptic): gemini-1.5-pro (kostenlos, Phase 1-2)
Phase 3+: claude-sonnet-4-6 für Extraktion
Swap: LLM_PROVIDER in .env → neue Epoch → nahtlos
NEVER: "latest" Alias. Immer gepinnte Versionen.
NEVER: Model-Wechsel ohne neue Epoch (INVARIANT-3).

## 2. Harness & Review
Review: ohara.py review (human) / Validator Agent (Phase 2+)
Gate: Skeptic-Cycle als Hard Gate vor EMERGING → VALIDATED
Evidence: cycle_vitality Records + Acceptance Rate Tracking

## 3. Infrastructure & Security
Hosting: Hetzner CX11 (€2.49/mo) — Phase 1-3
  Upgrade CX21 bei 5+ gleichzeitigen Wizards
Location: nbg1 (Nürnberg)
Tunnel: Tailscale — SSH nur via Tailscale IP
Firewall: DENY all inbound außer Port 22 via Tailscale
SSH: Ed25519 — Password Auth deaktiviert
Secrets: .env (gitignored) — NIEMALS in Code oder Chat

## 4. Application Stack
Language: Python 3.12
DB: SQLite (3 Dateien: vault/knowledge/governance)
  Phase 4+: PostgreSQL Migration
  Phase 5+: Neo4j Graph Layer (read-only)
CLI: Click + Rich
Scheduling: APScheduler → systemd Timer (VPS)
LLM SDK: google-generativeai (Phase 1-2), anthropic (Phase 3+)

## 5. Analytics & Operations
Monitoring: cycle_vitality Tabelle — Acceptance Rate, Anomalien
Vitality: Jeder Wizard-Cycle emittiert Vitality Record (Pflicht)
Cost: estimated_cost_usd pro Cycle tracken

## 6. Locked Versions
Runtime: Python 3.12
SQLite: Ubuntu 24.04 System-Version
Key Libs: click, rich, google-generativeai, python-dotenv

## 7. Anti-Patterns (NEVER DO)
NEVER: Model-Version ohne neue Epoch ändern
NEVER: API Keys in Code oder Chat
NEVER: Raw Vault Items löschen oder überschreiben
NEVER: STRUCTURAL Promotion automatisieren
NEVER: World 2 write-back direkt zu World 1
NEVER: Bestehende DB-Columns umbenennen/löschen (nur additive Changes)
NEVER: Duplikate von bestehenden Files erstellen — Originals updaten
