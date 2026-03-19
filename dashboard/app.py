#!/usr/bin/env python3
"""
OHARA Web Dashboard
Runs on VPS port 7842 (Tailscale-only)
Access: http://100.118.247.94:7842
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "scripts"))

from flask import Flask, jsonify, request, render_template_string
import db

app = Flask(__name__)

# ============================================================
# HTML TEMPLATE
# ============================================================

HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OHARA — Library of Agentic Wizards</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,400;0,500;1,300&family=JetBrains+Mono:wght@300;400&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0a0a0f;
  --bg2: #111118;
  --bg3: #1a1a24;
  --border: rgba(120,120,180,0.12);
  --border2: rgba(120,120,180,0.25);
  --text: #e8e8f0;
  --text2: #8888aa;
  --text3: #4a4a66;
  --gold: #c9a84c;
  --gold2: #e8c97a;
  --teal: #4ac9b0;
  --red: #c94a6a;
  --blue: #4a8bc9;
  --purple: #9b6ec9;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Header */
.header {
  border-bottom: 1px solid var(--border);
  padding: 1.5rem 2rem;
  display: flex;
  align-items: baseline;
  gap: 1.5rem;
  background: var(--bg2);
}
.header h1 {
  font-family: 'Fraunces', serif;
  font-size: 22px;
  font-weight: 300;
  color: var(--gold2);
  letter-spacing: 0.02em;
}
.header .sub {
  font-size: 11px;
  color: var(--text3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.epoch-badge {
  margin-left: auto;
  font-size: 10px;
  color: var(--text3);
  border: 1px solid var(--border);
  padding: 3px 10px;
  border-radius: 20px;
}

/* Layout */
.main { display: grid; grid-template-columns: 280px 1fr; min-height: calc(100vh - 65px); }

/* Sidebar */
.sidebar {
  border-right: 1px solid var(--border);
  padding: 1.5rem 0;
  background: var(--bg2);
}
.nav-section {
  padding: 0 1.5rem;
  margin-bottom: 1.5rem;
}
.nav-label {
  font-size: 10px;
  color: var(--text3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}
.nav-item {
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text2);
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}
.nav-item:hover { background: var(--bg3); color: var(--text); }
.nav-item.active { background: var(--bg3); color: var(--gold); border-left: 2px solid var(--gold); padding-left: 8px; }
.nav-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--text3); flex-shrink: 0; }
.nav-dot.active { background: var(--teal); box-shadow: 0 0 6px var(--teal); }

/* Wizard cards in sidebar */
.wizard-card {
  margin: 0 1rem 0.5rem;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  background: var(--bg);
}
.wizard-card:hover { border-color: var(--border2); background: var(--bg3); }
.wizard-name { font-family: 'Fraunces', serif; font-size: 14px; color: var(--text); font-weight: 300; }
.wizard-domain { font-size: 10px; color: var(--text3); margin-top: 2px; }
.wizard-status { display: flex; align-items: center; gap: 6px; margin-top: 6px; }
.pulse { width: 6px; height: 6px; border-radius: 50%; background: var(--teal); animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* Content */
.content { padding: 2rem; overflow-y: auto; }

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  transition: border-color 0.15s;
}
.stat-card:hover { border-color: var(--border2); }
.stat-label { font-size: 10px; color: var(--text3); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.stat-value { font-family: 'Fraunces', serif; font-size: 28px; font-weight: 300; color: var(--gold2); }
.stat-sub { font-size: 10px; color: var(--text3); margin-top: 3px; }

/* Section */
.section { margin-bottom: 2rem; }
.section-title {
  font-size: 11px;
  color: var(--text3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Atom review */
.atom-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 0.75rem;
  transition: all 0.15s;
}
.atom-card:hover { border-color: var(--border2); }
.atom-claim { font-size: 14px; color: var(--text); line-height: 1.6; margin-bottom: 10px; font-family: 'Fraunces', serif; font-weight: 300; }
.atom-meta { display: flex; gap: 10px; flex-wrap: wrap; }
.meta-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 20px;
  border: 1px solid var(--border);
  color: var(--text2);
}
.meta-badge.type { border-color: rgba(74,139,201,0.3); color: var(--blue); }
.meta-badge.spec-1, .meta-badge.spec-2 { border-color: rgba(74,201,176,0.3); color: var(--teal); }
.meta-badge.spec-3 { border-color: rgba(201,168,76,0.3); color: var(--gold); }
.meta-badge.spec-4, .meta-badge.spec-5 { border-color: rgba(201,74,106,0.3); color: var(--red); }
.atom-actions { display: flex; gap: 8px; margin-top: 12px; }
.btn {
  padding: 5px 16px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text2);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn:hover { background: var(--bg3); color: var(--text); }
.btn.accept { border-color: rgba(74,201,176,0.4); color: var(--teal); }
.btn.accept:hover { background: rgba(74,201,176,0.1); }
.btn.reject { border-color: rgba(201,74,106,0.4); color: var(--red); }
.btn.reject:hover { background: rgba(201,74,106,0.1); }
.btn.primary { border-color: rgba(201,168,76,0.5); color: var(--gold); }
.btn.primary:hover { background: rgba(201,168,76,0.1); }

/* Log terminal */
.terminal {
  background: #070710;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
  font-size: 12px;
  line-height: 1.7;
  color: #7777aa;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
}
.terminal .ok { color: var(--teal); }
.terminal .err { color: var(--red); }
.terminal .info { color: var(--gold); }

/* Empty state */
.empty { text-align: center; padding: 3rem; color: var(--text3); }
.empty-icon { font-size: 32px; margin-bottom: 1rem; opacity: 0.3; }

/* Toast */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 12px;
  color: var(--teal);
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s;
  z-index: 100;
}
.toast.show { opacity: 1; transform: translateY(0); }

/* Page sections */
.page { display: none; }
.page.active { display: block; }
</style>
</head>
<body>

<div class="header">
  <h1>OHARA</h1>
  <span class="sub">Library of Agentic Wizards</span>
  <span class="epoch-badge" id="epoch-label">Loading...</span>
</div>

<div class="main">
  <div class="sidebar">
    <div class="nav-section">
      <div class="nav-label">Navigation</div>
      <div class="nav-item active" onclick="showPage('dashboard')">
        <div class="nav-dot active"></div> Dashboard
      </div>
      <div class="nav-item" onclick="showPage('review')">
        <div class="nav-dot" id="review-dot"></div> Review Queue
      </div>
      <div class="nav-item" onclick="showPage('patterns')">
        <div class="nav-dot"></div> Patterns
      </div>
      <div class="nav-item" onclick="showPage('logs')">
        <div class="nav-dot"></div> Live Logs
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-label">Wizards</div>
    </div>
    <div id="wizard-list"></div>
  </div>

  <div class="content">

    <!-- DASHBOARD -->
    <div class="page active" id="page-dashboard">
      <div class="stats-grid" id="stats-grid">
        <div class="stat-card"><div class="stat-label">Raw Items</div><div class="stat-value" id="s-raw">—</div></div>
        <div class="stat-card"><div class="stat-label">Atoms Total</div><div class="stat-value" id="s-atoms">—</div></div>
        <div class="stat-card"><div class="stat-label">Accepted</div><div class="stat-value" id="s-accepted">—</div></div>
        <div class="stat-card"><div class="stat-label">Pending Review</div><div class="stat-value" id="s-pending">—</div><div class="stat-sub">needs your attention</div></div>
        <div class="stat-card"><div class="stat-label">Patterns</div><div class="stat-value" id="s-patterns">—</div></div>
        <div class="stat-card"><div class="stat-label">Books</div><div class="stat-value" id="s-books">—</div></div>
      </div>

      <div class="section">
        <div class="section-title">
          Actions
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn primary" onclick="runAllScouts()">▶ Run All Scouts</button>
          <button class="btn primary" onclick="runScout('aria')">▶ Run Aria</button>
          <button class="btn primary" onclick="runScout('marcus')">▶ Run Marcus</button>
          <button class="btn primary" onclick="runScout('nova')">▶ Run Nova</button>
          <button class="btn primary" onclick="runScout('sterling')">▶ Run Sterling</button>
          <button class="btn primary" onclick="runScout('reina')">▶ Run Reina</button>
        </div>
      </div>

      <div class="section">
        <div class="section-title">Last Scout Output</div>
        <div class="terminal" id="last-output">Waiting for scout cycle...</div>
      </div>
    </div>

    <!-- REVIEW -->
    <div class="page" id="page-review">
      <div class="section">
        <div class="section-title">
          Candidate Atoms — Review Queue
          <button class="btn" onclick="loadReview()">↻ Refresh</button>
        </div>
        <div id="review-list"></div>
      </div>
    </div>

    <!-- PATTERNS -->
    <div class="page" id="page-patterns">
      <div class="section">
        <div class="section-title">Patterns</div>
        <div id="patterns-list"></div>
      </div>
    </div>

    <!-- LOGS -->
    <div class="page" id="page-logs">
      <div class="section">
        <div class="section-title">
          Live Logs
          <button class="btn" onclick="loadLogs()">↻ Refresh</button>
        </div>
        <div class="terminal" id="logs-content">Loading...</div>
      </div>
    </div>

  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let currentPage = 'dashboard';

function showPage(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  event.currentTarget.classList.add('active');
  currentPage = page;
  if (page === 'review') loadReview();
  if (page === 'patterns') loadPatterns();
  if (page === 'logs') loadLogs();
}

function toast(msg, ok=true) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.color = ok ? 'var(--teal)' : 'var(--red)';
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

async function loadStats() {
  try {
    const r = await fetch('/api/stats');
    const d = await r.json();
    document.getElementById('s-raw').textContent = d.raw_items_total || 0;
    document.getElementById('s-atoms').textContent = d.atoms_total || 0;
    document.getElementById('s-accepted').textContent = d.atoms_accepted || 0;
    document.getElementById('s-pending').textContent = d.atoms_candidate || 0;
    document.getElementById('s-patterns').textContent = Object.values(d.patterns_by_status || {}).reduce((a,b)=>a+b,0);
    document.getElementById('s-books').textContent = d.books_total || 0;
    if (d.atoms_candidate > 0) document.getElementById('review-dot').style.background = 'var(--gold)';
    document.getElementById('epoch-label').textContent = d.epoch_id || '';
  } catch(e) {}
}

async function loadWizards() {
  try {
    const r = await fetch('/api/wizards');
    const wizards = await r.json();
    const el = document.getElementById('wizard-list');
    el.innerHTML = wizards.map(w => `
      <div class="wizard-card" onclick="runScout('${w.short_name}')">
        <div class="wizard-name">${w.name}</div>
        <div class="wizard-domain">${w.domain}</div>
        <div class="wizard-status">
          <div class="pulse"></div>
          <span style="font-size:10px;color:var(--text3)">active</span>
        </div>
      </div>
    `).join('');
  } catch(e) {}
}

async function runScout(wizard) {
  toast(`Starting ${wizard}...`);
  document.getElementById('last-output').textContent = `Running scout: ${wizard}...\n`;
  try {
    const r = await fetch('/api/scout/run', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({wizard})
    });
    const d = await r.json();
    document.getElementById('last-output').textContent = d.output || 'Done';
    toast(`${wizard} cycle complete — ${d.atoms_written || 0} atoms written`);
    loadStats();
  } catch(e) {
    toast('Error: ' + e.message, false);
  }
}

async function runAllScouts() {
  toast('Starting all scouts...');
  document.getElementById('last-output').textContent = 'Running all scouts...\n';
  try {
    const r = await fetch('/api/scout/run-all', {method:'POST'});
    const d = await r.json();
    document.getElementById('last-output').textContent = d.output || 'Done';
    toast(`All scouts complete — ${d.total_atoms || 0} atoms written`);
    loadStats();
  } catch(e) {
    toast('Error: ' + e.message, false);
  }
}

async function loadReview() {
  try {
    const r = await fetch('/api/atoms/candidates');
    const atoms = await r.json();
    const el = document.getElementById('review-list');
    if (!atoms.length) {
      el.innerHTML = '<div class="empty"><div class="empty-icon">✦</div>No atoms pending review</div>';
      return;
    }
    el.innerHTML = atoms.map(a => `
      <div class="atom-card" id="atom-${a.id}">
        <div class="atom-claim">${a.claim}</div>
        <div class="atom-meta">
          <span class="meta-badge type">${a.claim_type}</span>
          <span class="meta-badge spec-${a.speculation_level}">spec ${a.speculation_level}/5</span>
          <span class="meta-badge">conf ${a.confidence_score.toFixed(2)}</span>
          <span class="meta-badge">${a.domain}</span>
          ${JSON.parse(a.utility_vector||'[]').map(u=>`<span class="meta-badge">${u}</span>`).join('')}
        </div>
        <div class="atom-actions">
          <button class="btn accept" onclick="decideAtom('${a.id}', 'accept')">✓ Accept</button>
          <button class="btn reject" onclick="decideAtom('${a.id}', 'reject')">✗ Reject</button>
        </div>
      </div>
    `).join('');
  } catch(e) {}
}

async function decideAtom(id, decision) {
  try {
    const reason = decision === 'reject' ? (prompt('Rejection reason:') || 'No reason') : null;
    const r = await fetch('/api/atoms/decide', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({id, decision, reason})
    });
    const d = await r.json();
    if (d.ok) {
      document.getElementById('atom-' + id).style.opacity = '0.3';
      setTimeout(() => document.getElementById('atom-' + id)?.remove(), 500);
      toast(decision === 'accept' ? 'Atom accepted' : 'Atom rejected');
      loadStats();
    }
  } catch(e) {}
}

async function loadPatterns() {
  try {
    const r = await fetch('/api/patterns');
    const patterns = await r.json();
    const el = document.getElementById('patterns-list');
    if (!patterns.length) {
      el.innerHTML = '<div class="empty"><div class="empty-icon">✦</div>No patterns yet</div>';
      return;
    }
    const colors = {signal:'var(--text3)',emerging:'var(--gold)',validated:'var(--teal)',structural:'var(--purple)',deprecated:'var(--red)'};
    el.innerHTML = patterns.map(p => `
      <div class="atom-card">
        <div class="atom-claim">${p.title}</div>
        <div style="font-size:12px;color:var(--text2);margin-bottom:8px">${p.summary}</div>
        <div class="atom-meta">
          <span class="meta-badge" style="color:${colors[p.status]||'var(--text2)'}">${p.status}</span>
          <span class="meta-badge">${p.atom_count} atoms</span>
          <span class="meta-badge">${p.domain}</span>
          ${p.unresolved_strong_count > 0 ? `<span class="meta-badge" style="color:var(--red)">${p.unresolved_strong_count} unresolved CE</span>` : ''}
        </div>
      </div>
    `).join('');
  } catch(e) {}
}

async function loadLogs() {
  try {
    const r = await fetch('/api/logs');
    const d = await r.json();
    document.getElementById('logs-content').textContent = d.logs || 'No logs yet';
  } catch(e) {}
}

// Init
loadStats();
loadWizards();
setInterval(loadStats, 30000);
</script>
</body>
</html>'''

# ============================================================
# API ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/stats')
def api_stats():
    stats = db.library_stats()
    epoch = db.get_active_epoch()
    stats['epoch_id'] = epoch['id']
    return jsonify(stats)

@app.route('/api/wizards')
def api_wizards():
    wizards = db.list_active_wizards()
    return jsonify(wizards)

@app.route('/api/atoms/candidates')
def api_candidates():
    atoms = db.list_atoms(status='candidate', limit=50)
    return jsonify(atoms)

@app.route('/api/atoms/decide', methods=['POST'])
def api_decide():
    data = request.json
    atom_id = data['id']
    decision = data['decision']
    reason = data.get('reason', '')
    if decision == 'accept':
        db.accept_atom(atom_id, reviewer='god')
    else:
        db.reject_atom(atom_id, reason=reason or 'Rejected via dashboard', reviewer='god')
    return jsonify({'ok': True})

@app.route('/api/patterns')
def api_patterns():
    patterns = db.list_patterns()
    return jsonify(patterns)

@app.route('/api/scout/run', methods=['POST'])
def api_scout_run():
    data = request.json
    wizard = data.get('wizard', 'aria')
    try:
        result = subprocess.run(
            ['python3', 'agents/scouts/scout.py', wizard],
            capture_output=True, text=True, timeout=300,
            cwd='/opt/ohara',
            env={**__import__('os').environ, 'PYTHONPATH': '/opt/ohara/core/scripts'}
        )
        output = result.stdout + result.stderr
        # Count atoms written from output
        atoms_written = 0
        for line in output.split('\n'):
            if 'Atoms written:' in line:
                try:
                    atoms_written = int(line.split(':')[1].strip())
                except:
                    pass
        return jsonify({'output': output, 'atoms_written': atoms_written})
    except Exception as e:
        return jsonify({'output': str(e), 'atoms_written': 0})

@app.route('/api/scout/run-all', methods=['POST'])
def api_scout_run_all():
    try:
        result = subprocess.run(
            ['python3', 'core/scripts/run_all_scouts.py'],
            capture_output=True, text=True, timeout=600,
            cwd='/opt/ohara',
            env={**__import__('os').environ, 'PYTHONPATH': '/opt/ohara/core/scripts'}
        )
        output = result.stdout + result.stderr
        total_atoms = 0
        for line in output.split('\n'):
            if 'Atoms written:' in line:
                try:
                    total_atoms += int(line.split(':')[1].strip())
                except:
                    pass
        return jsonify({'output': output, 'total_atoms': total_atoms})
    except Exception as e:
        return jsonify({'output': str(e), 'total_atoms': 0})

@app.route('/api/logs')
def api_logs():
    log_file = Path('/opt/ohara/logs/scouts-run.log')
    if log_file.exists():
        lines = log_file.read_text().split('\n')
        return jsonify({'logs': '\n'.join(lines[-100:])})
    return jsonify({'logs': 'No logs yet'})

if __name__ == '__main__':
    print("OHARA Dashboard starting on port 7842...")
    print("Access: http://100.118.247.94:7842")
    app.run(host='0.0.0.0', port=7842, debug=False)
