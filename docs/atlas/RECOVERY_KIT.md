---
system: Atlas Vault OS
version: 3.1
date: March 19, 2026
status: ACTIVE / DYNAMIC
project: OHARA
---
# RECOVERY_KIT.md - Restoration Guide
# PROJECT: OHARA

## 1. Environment Setup
VPS: Hetzner CPX22, Ubuntu 24.04
  Public IP: 178.104.84.117
  Tailscale IP: 100.118.247.94
Runtime: Python 3.12 + venv (/opt/ohara/.venv)
Repo: github.com/Nnvvee96/OHARA (privat)

## 2. Account Restoration
GitHub: Nnvvee96/OHARA — ohara-deploy Token in secrets.env
Hetzner: console.hetzner.cloud → Projekt ohara → Server ohara-library
Tailscale: login.tailscale.com → ohara-library Device
Gemini: aistudio.google.com → API Key in /opt/ohara/.env
SSH: ~/.ssh/id_ohara (ohne Passwort, Ed25519)

## 3. Wiederherstellungs-Sequenz
1. Tailscale auf MacBook: tailscale up
2. SSH in VPS: ssh root@100.118.247.94
3. Status prüfen: cd /opt/ohara && PYTHONPATH=core/scripts .venv/bin/python3 core/scripts/ohara.py status
4. Logs: tail -f logs/scouts-run.log
5. Dashboard: http://100.118.247.94:7842
6. Services: systemctl status ohara-scouts.timer ohara-dashboard

Bei komplettem Neuaufbau:
1. cp secrets.example secrets.env && befüllen
2. python deploy.py (provisioniert alles automatisch)

## 4. Nach Code-Änderungen (Update-Workflow)
Claude pusht zu GitHub →
Du führst aus:
  ssh root@100.118.247.94 'cd /opt/ohara && git pull && systemctl restart ohara-scouts.timer ohara-dashboard'

Geplant (Webhook): Auto-Pull ohne manuellen Befehl.

## 5. Backup
Täglich auf VPS:
  cp core/db/ohara_vault.db backup/vault_$(date +%Y%m%d).db
  cp core/db/ohara_knowledge.db backup/knowledge_$(date +%Y%m%d).db
  cp core/db/ohara_governance.db backup/governance_$(date +%Y%m%d).db

## 6. Diagnostics
Reddit 403 → HackerNews RSS verwenden
SSH encrypted key → ssh-keygen -N "" oder ssh-add
Server deprecated type → cpx22 verwenden
Port nicht erreichbar → ufw allow in on tailscale0 to any port XXXX
Dashboard lädt nicht → systemctl restart ohara-dashboard
Scouts schreiben 0 Atome → Quellen prüfen, .env Gemini Key prüfen
