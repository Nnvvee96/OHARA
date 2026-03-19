---
system: Atlas Vault OS
version: 3.1
date: March 18, 2026
status: TEMPLATE / DYNAMIC
project: OHARA
---
# RECOVERY_KIT.md - Restoration Guide
# PROJECT: OHARA

## 1. Environment Setup
Infra: Hetzner CX11 VPS (Ubuntu 24.04) + Tailscale + UFW
Runtime: Python 3.12 + venv
Repo: github.com/[USERNAME]/ohara (privat)
Deploy: python deploy.py (einmalig neu provisionieren)

## 2. Account Restoration
GitHub: privates Repo "ohara" + PAT Token (repo scope)
Hetzner: console.hetzner.cloud → Projekt "ohara" → API Token (Read+Write)
Tailscale: login.tailscale.com → Auth Key (Reusable, nicht Ephemeral)
Gemini: aistudio.google.com → API Key (Free Tier)
SSH: ~/.ssh/id_ed25519 (privat) + id_ed25519.pub (für Hetzner)

Keys: Alle in secrets.env — niemals woanders.
  Verloren: Neu generieren → secrets.env updaten → neuer Epoch.

## 3. Sequence
1. secrets.env befüllen (cp secrets.example secrets.env)
2. python deploy.py → VPS provisioniert, gehärtet, Scouts gestartet
3. SSH via Tailscale: ssh root@<tailscale-ip>
4. cd /opt/ohara && PYTHONPATH=core/scripts .venv/bin/python ohara.py status
5. Vitality prüfen: tail -f logs/scouts-run.log
6. God Digest: ohara.py god digest

Update nach Code-Änderung:
  git add . && git commit -m "..." && git push
  ssh root@<tailscale-ip> 'cd /opt/ohara && git pull && systemctl restart ohara-scouts.timer'

## 4. Backup & Restore
Backup (täglich auf VPS):
  cp core/db/ohara_vault.db backup/vault_$(date +%Y%m%d).db
  cp core/db/ohara_knowledge.db backup/knowledge_$(date +%Y%m%d).db
  cp core/db/ohara_governance.db backup/governance_$(date +%Y%m%d).db
Restore: .db Datei zurückkopieren — SQLite ist self-contained.

## 5. Diagnostics
Hohe Uptime, geringe Output → Prompt-Problem oder Domain-Exhaustion
  → cycle_vitality prüfen, acceptance_rate letzte 10 Cycles
  → Prompt updaten (neue Epoch), Quellen erweitern

Wizard schweigt (>72h) → Infrastruktur-Problem
  → systemctl status ohara-scouts.timer
  → tail logs/scout-[wizard].log
  → Tailscale Verbindung prüfen

Hohe Duplikat-Rate (>80%) → Source Pool erschöpft
  → duplicate_rate in cycle_vitality
  → Neue Quellen hinzufügen (neue Epoch)

Anomalie-Severity CRITICAL → ohara.py god digest sofort prüfen
