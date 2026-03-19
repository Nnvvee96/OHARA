---
system: Atlas Vault OS
version: 1.0
date: March 18, 2026
status: TEMPLATE / DYNAMIC
project: OHARA
---
# RECOVERY_KIT.md - Restoration Guide
# PROJECT: OHARA

## 1. Environment Setup
Infra: Hetzner CX11 VPS (Ubuntu 24.04) + Tailscale
Runtime: Python 3.12 + venv
Harness: 31 Schema-Tests (test_schema.py)
Repo: github.com/[USERNAME]/ohara (privat)

## 2. Account Restoration
GitHub: Privates Repo "ohara" + PAT Token
Hetzner: console.hetzner.cloud → Projekt "ohara" → API Token
Tailscale: login.tailscale.com → Auth Key (Reusable, not Ephemeral)
Gemini: aistudio.google.com → API Key (Free Tier)
Alle Keys: secrets.env — niemals woanders

## 3. Sequence
1. secrets.env befüllen (cp secrets.example secrets.env)
2. python deploy.py → provisioniert alles automatisch
3. SSH: ssh root@<tailscale-ip>
4. Prüfen: cd /opt/ohara && PYTHONPATH=core/scripts .venv/bin/python ohara.py status
5. Logs: tail -f logs/scouts-run.log
6. Scouts: systemctl status ohara-scouts.timer

Update nach Code-Änderung:
  git add . && git commit -m "..." && git push
  ssh root@<tailscale-ip> 'cd /opt/ohara && git pull && systemctl restart ohara-scouts.timer'

## 4. Diagnostics
Hohe Uptime + geringe Output = Prompt-Problem oder Domain-Exhaustion
  → cycle_vitality prüfen, acceptance_rate letzte 10 Cycles
  → Prompt updaten (neue Epoch), Signal-Quellen erweitern

Wizard schweigt (72h+) = Infrastruktur-Problem
  → systemctl status ohara-scouts.timer
  → tail logs/scout-[wizard].log
  → Tailscale Verbindung prüfen

Hohe Duplikat-Rate = Signal-Pool erschöpft
  → duplicate_rate in cycle_vitality
  → Neue Quellen hinzufügen (neue Epoch)
