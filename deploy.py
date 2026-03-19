#!/usr/bin/env python3
"""
OHARA — One-Command Deploy Script
Provisions a Hetzner VPS, hardens it, installs OHARA, starts scouts.

Usage:
  python deploy.py

Requirements:
  pip install requests paramiko python-dotenv

Run from project root. secrets.env must exist and be filled in.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from dotenv import dotenv_values

# ─────────────────────────────────────────────────────────────
# LOAD SECRETS
# ─────────────────────────────────────────────────────────────

SECRETS_FILE = Path(__file__).parent / "secrets.env"

if not SECRETS_FILE.exists():
    print("\n  ERROR: secrets.env not found.")
    print("  Run: cp secrets.example secrets.env")
    print("  Then fill in all values.\n")
    sys.exit(1)

cfg = dotenv_values(SECRETS_FILE)

REQUIRED = [
    "HETZNER_API_TOKEN", "TAILSCALE_AUTH_KEY",
    "GITHUB_USERNAME", "GITHUB_TOKEN",
    "GEMINI_API_KEY", "SSH_PUBLIC_KEY_PATH",
]

missing = [k for k in REQUIRED if not cfg.get(k) or "your_" in cfg.get(k, "")]
if missing:
    print(f"\n  ERROR: Fill in secrets.env — missing or unfilled: {missing}\n")
    sys.exit(1)

HETZNER_TOKEN    = cfg["HETZNER_API_TOKEN"]
TAILSCALE_KEY    = cfg["TAILSCALE_AUTH_KEY"]
GITHUB_USER      = cfg["GITHUB_USERNAME"]
GITHUB_TOKEN     = cfg["GITHUB_TOKEN"]
GEMINI_KEY       = cfg["GEMINI_API_KEY"]
SSH_KEY_PATH     = Path(cfg["SSH_PUBLIC_KEY_PATH"]).expanduser()
SERVER_TYPE      = cfg.get("HETZNER_SERVER_TYPE", "cx22")
LOCATION         = cfg.get("HETZNER_LOCATION", "nbg1")
SCOUT_INTERVAL   = cfg.get("SCOUT_INTERVAL_SECONDS", "3600")
MAX_SOURCES      = cfg.get("SCOUT_MAX_SOURCES_PER_CYCLE", "10")
MAX_ATOMS        = cfg.get("SCOUT_MAX_ATOMS_PER_SOURCE", "5")
REPO_NAME        = "ohara"

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

try:
    import requests
    import paramiko
except ImportError:
    print("\n  Installing deploy dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "requests", "paramiko", "python-dotenv", "-q"])
    import requests
    import paramiko

def hetzner(method: str, path: str, data: dict = None):
    r = requests.request(
        method,
        f"https://api.hetzner.cloud/v1{path}",
        headers={
            "Authorization": f"Bearer {HETZNER_TOKEN}",
            "Content-Type": "application/json",
        },
        json=data,
        timeout=30,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"Hetzner API error {r.status_code}: {r.text}")
    return r.json()

def step(msg: str):
    print(f"\n  ▸ {msg}")

def ok(msg: str):
    print(f"    ✓ {msg}")

def wait_for_ssh(ip: str, timeout: int = 120) -> bool:
    import socket
    start = time.time()
    while time.time() - start < timeout:
        try:
            s = socket.create_connection((ip, 22), timeout=5)
            s.close()
            return True
        except Exception:
            time.sleep(5)
    return False

def ssh_run(client: paramiko.SSHClient, cmd: str, check: bool = True) -> str:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if check and exit_code != 0:
        raise RuntimeError(f"SSH command failed (exit {exit_code}):\n{cmd}\n{err}")
    return out

def ssh_connect(ip: str, retries: int = 8) -> paramiko.SSHClient:
    key_path = SSH_KEY_PATH.with_suffix("")  # private key = no .pub
    for i in range(retries):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                ip, port=22, username="root",
                key_filename=str(key_path),
                timeout=15,
            )
            return client
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(10)

# ─────────────────────────────────────────────────────────────
# SERVER SETUP SCRIPT (runs on VPS)
# ─────────────────────────────────────────────────────────────

def build_setup_script(
    tailscale_key: str,
    github_user: str,
    github_token: str,
    gemini_key: str,
    scout_interval: str,
    max_sources: str,
    max_atoms: str,
) -> str:
    """Build the bash script that runs on the VPS after provisioning."""

    return f"""#!/bin/bash
set -e

echo "═══════════════════════════════════════"
echo " OHARA VPS Setup"
echo "═══════════════════════════════════════"

# ── System update ─────────────────────────────────────────
echo "[1/8] System update..."
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq git python3 python3-pip python3-venv curl ufw

# ── Tailscale ─────────────────────────────────────────────
echo "[2/8] Installing Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up --authkey={tailscale_key} --hostname=ohara-library
TAILSCALE_IP=$(tailscale ip -4)
echo "  Tailscale IP: $TAILSCALE_IP"

# ── Firewall: Tailscale-only SSH ──────────────────────────
echo "[3/8] Hardening firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow in on tailscale0 to any port 22
ufw --force enable
echo "  Firewall: SSH only via Tailscale"

# ── Disable password auth ─────────────────────────────────
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl reload sshd
echo "  SSH: password auth disabled"

# ── Clone repo ────────────────────────────────────────────
echo "[4/8] Cloning OHARA repository..."
cd /opt
git clone https://{github_token}@github.com/{github_user}/{REPO_NAME}.git ohara
cd /opt/ohara

# ── Python environment ────────────────────────────────────
echo "[5/8] Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -q click rich google-generativeai python-dotenv requests

# ── Write .env ────────────────────────────────────────────
echo "[6/8] Writing environment config..."
cat > /opt/ohara/.env << 'ENVEOF'
LLM_PROVIDER=gemini
GEMINI_API_KEY={gemini_key}
ANTHROPIC_API_KEY=
LLM_MODEL_EXTRACTION=gemini-1.5-flash
LLM_MODEL_REASONING=gemini-1.5-pro
SCOUT_CYCLE_DELAY_SECONDS=2
SCOUT_MAX_SOURCES_PER_CYCLE={max_sources}
SCOUT_MAX_ATOMS_PER_SOURCE={max_atoms}
ENVEOF

# ── Initialize databases ──────────────────────────────────
echo "[7/8] Initializing databases..."
source .venv/bin/activate
PYTHONPATH=/opt/ohara/core/scripts python3 core/db/migrations/migrate.py
PYTHONPATH=/opt/ohara/core/scripts python3 core/db/seed/seed.py

# ── Systemd services ──────────────────────────────────────
echo "[8/8] Installing scout services..."

# One service per wizard
for WIZARD in aria marcus nova sterling reina; do

cat > /etc/systemd/system/ohara-scout-$WIZARD.service << SVCEOF
[Unit]
Description=OHARA Scout — $WIZARD
After=network.target tailscaled.service
Wants=tailscaled.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ohara
Environment=PYTHONPATH=/opt/ohara/core/scripts
ExecStart=/opt/ohara/.venv/bin/python3 agents/scouts/scout.py $WIZARD
Restart=always
RestartSec={scout_interval}
StandardOutput=append:/opt/ohara/logs/scout-$WIZARD.log
StandardError=append:/opt/ohara/logs/scout-$WIZARD.log

[Install]
WantedBy=multi-user.target
SVCEOF

done

# Scheduled runner (runs all scouts on interval)
cat > /etc/systemd/system/ohara-scouts.timer << TIMEREOF
[Unit]
Description=OHARA Scout Cycle Timer

[Timer]
OnBootSec=5min
OnUnitActiveSec={scout_interval}s
Unit=ohara-scouts-run.service

[Install]
WantedBy=timers.target
TIMEREOF

cat > /etc/systemd/system/ohara-scouts-run.service << RUNEOF
[Unit]
Description=OHARA — Run All Scout Cycles

[Service]
Type=oneshot
WorkingDirectory=/opt/ohara
Environment=PYTHONPATH=/opt/ohara/core/scripts
ExecStart=/opt/ohara/.venv/bin/python3 core/scripts/run_all_scouts.py
StandardOutput=append:/opt/ohara/logs/scouts-run.log
StandardError=append:/opt/ohara/logs/scouts-run.log
RUNEOF

mkdir -p /opt/ohara/logs
systemctl daemon-reload
systemctl enable ohara-scouts.timer
systemctl start ohara-scouts.timer

echo ""
echo "═══════════════════════════════════════"
echo " OHARA Setup Complete"
echo " Tailscale IP: $TAILSCALE_IP"
echo " Scouts: scheduled every {scout_interval}s"
echo " Logs: /opt/ohara/logs/"
echo " Update: cd /opt/ohara && git pull"
echo "═══════════════════════════════════════"
"""

# ─────────────────────────────────────────────────────────────
# GITHUB REPO SETUP
# ─────────────────────────────────────────────────────────────

def ensure_github_repo():
    """Check if repo exists on GitHub, create if not."""
    step("Checking GitHub repository...")

    r = requests.get(
        f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}",
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
    )

    if r.status_code == 200:
        ok(f"Repository exists: github.com/{GITHUB_USER}/{REPO_NAME}")
        return

    if r.status_code == 404:
        step("Creating private GitHub repository...")
        r2 = requests.post(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={
                "name": REPO_NAME,
                "private": True,
                "description": "OHARA — The Library of Agentic Wizards",
                "auto_init": False,
            }
        )
        if r2.status_code == 201:
            ok(f"Repository created: github.com/{GITHUB_USER}/{REPO_NAME}")
        else:
            raise RuntimeError(f"GitHub repo creation failed: {r2.text}")
    else:
        raise RuntimeError(f"GitHub API error: {r.status_code}")

def push_to_github():
    """Initialize git and push current codebase to GitHub."""
    step("Pushing codebase to GitHub...")

    project_dir = Path(__file__).parent

    # Check if already a git repo
    if not (project_dir / ".git").exists():
        subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin",
             f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{REPO_NAME}.git"],
            cwd=project_dir, check=True, capture_output=True
        )
    else:
        # Update remote URL with token
        subprocess.run(
            ["git", "remote", "set-url", "origin",
             f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{REPO_NAME}.git"],
            cwd=project_dir, check=True, capture_output=True
        )

    subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)

    result = subprocess.run(
        ["git", "commit", "-m", "OHARA Phase 0 — initial commit"],
        cwd=project_dir, capture_output=True
    )
    # Ignore if nothing to commit
    if result.returncode not in (0, 1):
        raise RuntimeError(f"Git commit failed: {result.stderr.decode()}")

    subprocess.run(
        ["git", "branch", "-M", "main"],
        cwd=project_dir, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "push", "-u", "origin", "main", "--force"],
        cwd=project_dir, check=True, capture_output=True
    )
    ok("Pushed to GitHub")

# ─────────────────────────────────────────────────────────────
# MAIN DEPLOY
# ─────────────────────────────────────────────────────────────

def deploy():
    print("\n" + "═"*50)
    print(" OHARA — Deploy")
    print("═"*50)

    # 1. GitHub
    ensure_github_repo()
    push_to_github()

    # 2. SSH key
    step("Reading SSH public key...")
    if not SSH_KEY_PATH.exists():
        print(f"\n  ERROR: SSH public key not found at {SSH_KEY_PATH}")
        print("  Generate one with: ssh-keygen -t ed25519 -C 'ohara'")
        sys.exit(1)
    ssh_pub_key = SSH_KEY_PATH.read_text().strip()
    ok(f"SSH key loaded: {SSH_KEY_PATH.name}")

    # 3. Register SSH key with Hetzner
    step("Registering SSH key with Hetzner...")
    existing_keys = hetzner("GET", "/ssh_keys")
    key_id = None
    for k in existing_keys.get("ssh_keys", []):
        if k["public_key"].strip() == ssh_pub_key:
            key_id = k["id"]
            ok(f"Key already registered (id={key_id})")
            break

    if not key_id:
        try:
            result = hetzner("POST", "/ssh_keys", {
                "name": "ohara-deploy",
                "public_key": ssh_pub_key
            })
            key_id = result["ssh_key"]["id"]
            ok(f"SSH key registered (id={key_id})")
        except RuntimeError as e:
            if "uniqueness_error" in str(e) or "409" in str(e):
                # Key exists — find by comparing type+base64 (ignore comment/trailing whitespace)
                all_keys = hetzner("GET", "/ssh_keys")
                local_core = " ".join(ssh_pub_key.strip().split()[:2])
                for k in all_keys.get("ssh_keys", []):
                    remote_core = " ".join(k["public_key"].strip().split()[:2])
                    if remote_core == local_core:
                        key_id = k["id"]
                        ok(f"SSH key already exists, reusing (id={key_id}, name={k['name']})")
                        break
                if not key_id:
                    # Fallback: use first available key
                    keys_list = all_keys.get("ssh_keys", [])
                    if keys_list:
                        key_id = keys_list[0]["id"]
                        ok(f"Using existing SSH key (id={key_id}, name={keys_list[0]['name']})")
                    else:
                        raise RuntimeError("No SSH keys found on Hetzner account.")
            else:
                raise

    # 4. Provision VPS
    step(f"Provisioning Hetzner server in {LOCATION}...")
    
    # First check available server types
    available = hetzner("GET", "/server_types")
    available_names = [st["name"] for st in available.get("server_types", []) 
                      if not st.get("deprecated", False)]
    
    # Pick best available type
    preferred = ["cpx22", "cpx21", "cx22", "cpx32", "cx32"]
    chosen_type = SERVER_TYPE
    for p in preferred:
        if p in available_names:
            chosen_type = p
            break
    
    # Check if server already exists
    server_id = None
    server_ip = None
    existing_servers = hetzner("GET", "/servers")
    for s in existing_servers.get("servers", []):
        if s["name"] == "ohara-library":
            server_id = s["id"]
            server_ip = s["public_net"]["ipv4"]["ip"]
            ok(f"Server already exists — reusing (id={server_id}, ip={server_ip})")
            break

    if not server_id:
        ok(f"Using server type: {chosen_type}")
        server_result = hetzner("POST", "/servers", {
            "name": "ohara-library",
            "server_type": chosen_type,
            "location": LOCATION,
            "image": "ubuntu-24.04",
            "ssh_keys": [key_id],
            "labels": {"project": "ohara", "role": "library"},
        })
        server = server_result["server"]
        server_id = server["id"]
        server_ip = server["public_net"]["ipv4"]["ip"]
        ok(f"Server created — ID: {server_id}, IP: {server_ip}")

    # 5. Wait for boot
    step("Waiting for server to boot...")
    time.sleep(20)
    if not wait_for_ssh(server_ip, timeout=120):
        raise RuntimeError("Server SSH never became available. Check Hetzner console.")
    ok("Server is up and accepting SSH")

    # 6. Connect and run setup
    step("Connecting via SSH...")
    client = ssh_connect(server_ip)
    ok("Connected")

    step("Running setup script on VPS (this takes 3-5 minutes)...")
    setup_script = build_setup_script(
        tailscale_key=TAILSCALE_KEY,
        github_user=GITHUB_USER,
        github_token=GITHUB_TOKEN,
        gemini_key=GEMINI_KEY,
        scout_interval=SCOUT_INTERVAL,
        max_sources=MAX_SOURCES,
        max_atoms=MAX_ATOMS,
    )

    # Write and execute setup script
    ssh_run(client, f"cat > /tmp/ohara_setup.sh << 'SCRIPTEOF'\n{setup_script}\nSCRIPTEOF")
    ssh_run(client, "chmod +x /tmp/ohara_setup.sh")

    # Stream output
    stdin, stdout, stderr = client.exec_command("bash /tmp/ohara_setup.sh", timeout=600)
    for line in stdout:
        print(f"    {line.rstrip()}")

    exit_code = stdout.channel.recv_exit_status()
    if exit_code != 0:
        err = stderr.read().decode()
        raise RuntimeError(f"Setup script failed:\n{err}")

    # 7. Get Tailscale IP
    tailscale_ip = ssh_run(client, "tailscale ip -4", check=False)

    client.close()

    # 8. Save server info locally
    server_info = {
        "server_id": server_id,
        "public_ip": server_ip,
        "tailscale_ip": tailscale_ip,
        "location": LOCATION,
        "type": SERVER_TYPE,
        "deployed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    Path("server.json").write_text(json.dumps(server_info, indent=2))

    # ─── Success ──────────────────────────────────────────────
    print("\n" + "═"*50)
    print(" OHARA — Deploy Complete")
    print("═"*50)
    print(f"\n  Public IP:     {server_ip}")
    print(f"  Tailscale IP:  {tailscale_ip or '(check tailscale admin)'}")
    print(f"\n  SSH access:")
    print(f"    ssh root@{tailscale_ip or server_ip}")
    print(f"\n  Scout logs:")
    print(f"    ssh root@{tailscale_ip} 'tail -f /opt/ohara/logs/scouts-run.log'")
    print(f"\n  Update OHARA after code changes:")
    print(f"    ssh root@{tailscale_ip} 'cd /opt/ohara && git pull && systemctl restart ohara-scouts.timer'")
    print(f"\n  Library status (from VPS):")
    print(f"    ssh root@{tailscale_ip} 'cd /opt/ohara && PYTHONPATH=core/scripts .venv/bin/python3 core/scripts/ohara.py status'")
    print(f"\n  Server info saved to: server.json")
    print("═"*50 + "\n")


if __name__ == "__main__":
    deploy()
