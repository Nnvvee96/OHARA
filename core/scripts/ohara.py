#!/usr/bin/env python3
"""
OHARA CLI — The God Interface & Wizard Workbench
Phase 1: Manual operation commands for human librarians.

Usage:
  python ohara.py status
  python ohara.py ingest --wizard aria --url https://...
  python ohara.py atom create --wizard aria
  python ohara.py atom list --domain ai_patterns
  python ohara.py review --wizard aria
  python ohara.py pattern create --wizard aria
  python ohara.py god digest
  python ohara.py god approve --pattern <id>
"""

import sys
import json
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import box
from rich.text import Text

import db

console = Console()

CLAIM_TYPES = [
    "trend", "tactic", "structural_shift", "failure_mode",
    "metric", "principle", "speculation", "observation"
]

SOURCE_TIERS = ["primary", "secondary", "aggregator", "social", "internal"]

# ============================================================
# ROOT
# ============================================================

@click.group()
def cli():
    """OHARA — The Library of Agentic Wizards\n\nEpistemic knowledge infrastructure."""
    pass

# ============================================================
# STATUS
# ============================================================

@cli.command()
def status():
    """Library status — overview of all active systems."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]OHARA[/bold cyan] — The Library of Agentic Wizards",
        border_style="cyan"
    ))

    # Epoch
    try:
        epoch = db.get_active_epoch()
        console.print(f"\n[dim]Epoch:[/dim] [yellow]{epoch['id']}[/yellow] ({epoch['name']})")
        thresholds = json.loads(epoch['scoring_thresholds'])
        s_to_e = thresholds.get('signal_to_emerging', {})
        status_label = s_to_e.get('status', 'UNKNOWN')
        color = "red" if "PENDING" in status_label else "green"
        console.print(f"[dim]Thresholds:[/dim] [{color}]{status_label}[/{color}]")
    except Exception as e:
        console.print(f"[red]Epoch error: {e}[/red]")

    # Wizards
    wizards = db.list_active_wizards()
    console.print(f"\n[bold]Active Wizards ({len(wizards)})[/bold]")
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold dim")
    t.add_column("Name", style="cyan")
    t.add_column("Domain")
    t.add_column("Specialty", max_width=50)
    for w in wizards:
        t.add_row(w['name'], w['domain'], w['specialty'])
    console.print(t)

    # Library stats
    stats = db.library_stats()
    console.print("[bold]Library State[/bold]")
    t2 = Table(box=box.SIMPLE, show_header=False)
    t2.add_column("Metric", style="dim")
    t2.add_column("Value", style="bold")
    t2.add_row("Raw items", str(stats['raw_items_total']))
    t2.add_row("Atoms (total)", str(stats['atoms_total']))
    t2.add_row("Atoms (accepted)", str(stats.get('atoms_accepted', 0)))
    t2.add_row("Atoms (pending review)", str(stats.get('atoms_candidate', 0)))
    t2.add_row("Books", str(stats['books_total']))
    t2.add_row("Counter-evidence (unresolved)", str(stats['counter_evidence_unresolved']))

    by_status = stats.get('patterns_by_status', {})
    for s in ['signal', 'emerging', 'validated', 'structural', 'deprecated']:
        if s in by_status:
            t2.add_row(f"Patterns ({s})", str(by_status[s]))
    console.print(t2)
    console.print()

# ============================================================
# INGEST
# ============================================================

@cli.command()
@click.option('--wizard', '-w', required=True, help='Wizard short name (e.g. aria)')
@click.option('--url', '-u', required=True, help='URL to ingest')
@click.option('--tier', '-t', default='secondary',
              type=click.Choice(SOURCE_TIERS), help='Source tier')
@click.option('--independence', '-i', default=0.5, type=float,
              help='Editorial independence score 0.0-1.0')
def ingest(wizard, url, tier, independence):
    """Ingest a raw source URL into the vault."""
    import urllib.request
    import urllib.error

    wiz = db.get_wizard(wizard)
    if not wiz:
        console.print(f"[red]Wizard '{wizard}' not found or inactive.[/red]")
        sys.exit(1)

    epoch = db.get_active_epoch(wiz['id'])

    console.print(f"\n[dim]Wizard:[/dim] [cyan]{wiz['name']}[/cyan] ({wiz['domain']})")
    console.print(f"[dim]URL:[/dim] {url}")
    console.print(f"[dim]Fetching...[/dim]")

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'OHARA/1.0 knowledge-librarian'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            content_type_header = resp.headers.get('Content-Type', 'text/html')
    except urllib.error.URLError as e:
        console.print(f"[red]Fetch failed: {e}[/red]")
        sys.exit(1)

    # Detect content type
    if 'pdf' in content_type_header:
        ctype = 'pdf'
    elif 'json' in content_type_header:
        ctype = 'json'
    else:
        ctype = 'html'

    size_kb = len(content) / 1024
    console.print(f"[dim]Content:[/dim] {ctype} — {size_kb:.1f} KB")

    raw_id, is_new = db.insert_raw_item(
        origin_url=url,
        domain=wiz['domain'],
        content=content,
        content_type=ctype,
        source_tier=tier,
        ingestion_agent=f"wiz_{wizard}",
        epoch_id=epoch['id'],
        editorial_independence=independence,
    )

    if is_new:
        console.print(f"\n[green]✓ Ingested[/green] — ID: [yellow]{raw_id}[/yellow]")
        console.print(f"\n[dim]Next:[/dim] ohara atom create --wizard {wizard} --raw {raw_id}")
    else:
        console.print(f"\n[yellow]⚠ Duplicate[/yellow] — already in vault: [yellow]{raw_id}[/yellow]")

    console.print()

# ============================================================
# ATOM
# ============================================================

@cli.group()
def atom():
    """Atom management — create, review, list."""
    pass

@atom.command('create')
@click.option('--wizard', '-w', required=True, help='Wizard short name')
@click.option('--raw', '-r', required=True, help='Raw item ID this atom is extracted from')
def atom_create(wizard, raw):
    """Interactively extract an atom from a raw source."""
    wiz = db.get_wizard(wizard)
    if not wiz:
        console.print(f"[red]Wizard '{wizard}' not found.[/red]")
        sys.exit(1)

    epoch = db.get_active_epoch(wiz['id'])

    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Atom Extraction[/bold cyan]\n"
        f"Wizard: [cyan]{wiz['name']}[/cyan] | Domain: {wiz['domain']}\n"
        f"Source: [dim]{raw}[/dim]",
        border_style="dim"
    ))
    console.print(
        "\n[bold]Persona reminder:[/bold]\n"
        f"[dim italic]{wiz['persona_summary']}[/dim italic]\n"
    )

    # Claim
    console.print("[bold]Step 1 — The Claim[/bold]")
    console.print("[dim]Write a single, specific claim. Max 280 characters. No vague generalities.[/dim]")
    while True:
        claim = Prompt.ask("\nClaim")
        if len(claim) > 280:
            console.print(f"[red]Too long ({len(claim)} chars). Max 280.[/red]")
        elif len(claim) < 20:
            console.print(f"[yellow]Too short ({len(claim)} chars). Be specific.[/yellow]")
        else:
            console.print(f"[dim]{len(claim)}/280 characters[/dim]")
            break

    # Claim type
    console.print("\n[bold]Step 2 — Claim Type[/bold]")
    for i, ct in enumerate(CLAIM_TYPES, 1):
        console.print(f"  [cyan]{i}[/cyan]. {ct}")
    while True:
        choice = IntPrompt.ask("\nType (1-8)")
        if 1 <= choice <= len(CLAIM_TYPES):
            claim_type = CLAIM_TYPES[choice - 1]
            break
        console.print("[red]Invalid choice.[/red]")

    # Speculation level
    console.print("\n[bold]Step 3 — Speculation Level[/bold]")
    console.print("  [cyan]1[/cyan] = Strong evidence (multiple independent sources, tested)")
    console.print("  [cyan]2[/cyan] = Good evidence (solid sourcing, plausible mechanism)")
    console.print("  [cyan]3[/cyan] = Moderate (some evidence, mechanism unclear)")
    console.print("  [cyan]4[/cyan] = Weak (anecdotal, limited sourcing)")
    console.print("  [cyan]5[/cyan] = Pure speculation (hypothesis, no real evidence)")
    while True:
        spec = IntPrompt.ask("\nSpeculation level (1-5)")
        if 1 <= spec <= 5:
            break
        console.print("[red]Must be 1-5.[/red]")

    # Confidence score
    console.print("\n[bold]Step 4 — Confidence Score[/bold]")
    console.print("[dim]0.0 = no confidence | 1.0 = absolute certainty[/dim]")
    console.print("[dim]Be honest. Overconfidence is an epistemic failure.[/dim]")
    while True:
        conf_str = Prompt.ask("\nConfidence (0.0 - 1.0)")
        try:
            conf = float(conf_str)
            if 0.0 <= conf <= 1.0:
                break
            console.print("[red]Must be between 0.0 and 1.0.[/red]")
        except ValueError:
            console.print("[red]Enter a decimal number.[/red]")

    # Cross-domain tags
    console.print("\n[bold]Step 5 — Cross-Domain Resonance[/bold]")
    console.print("[dim]Does this atom apply to other domains? List them (comma-separated) or press Enter to skip.[/dim]")
    console.print(f"[dim]Available: ai_patterns, software_architecture, saas_product, finance_investing, marketing_distribution[/dim]")
    xd_raw = Prompt.ask("\nCross-domain tags", default="")
    cross_tags = [t.strip() for t in xd_raw.split(",") if t.strip()] if xd_raw else []

    # Utility vector
    UTILITY_OPTIONS = [
        "product_building",
        "process_improvement",
        "system_enhancement",
        "financial",
        "future_optionality",
        "personal_capability",
        "creative_enabling",
        "decision_support",
    ]
    console.print("\n[bold]Step 6 — Utility Vector[/bold]")
    console.print("[dim]What could this knowledge be useful for? Select all that apply.[/dim]")
    console.print("[dim]If none apply even speculatively → consider rejecting this atom.[/dim]\n")
    for i, u in enumerate(UTILITY_OPTIONS, 1):
        console.print(f"  [cyan]{i}[/cyan]. {u}")
    console.print()
    uv_raw = Prompt.ask("Numbers (comma-separated, e.g. 1,3,5)", default="")
    utility_vector = []
    if uv_raw.strip():
        for part in uv_raw.split(","):
            try:
                idx = int(part.strip()) - 1
                if 0 <= idx < len(UTILITY_OPTIONS):
                    utility_vector.append(UTILITY_OPTIONS[idx])
            except ValueError:
                pass

    if not utility_vector:
        console.print("[yellow]⚠ No utility vector selected. This atom has no identified potential use.[/yellow]")
        if not Confirm.ask("Proceed anyway?"):
            console.print("[dim]Cancelled. Consider rejecting this source.[/dim]")
            return

    # Review before commit
    console.print()
    console.print(Panel(
        f"[bold]Claim:[/bold] {claim}\n"
        f"[bold]Type:[/bold] {claim_type}\n"
        f"[bold]Speculation:[/bold] {spec}/5\n"
        f"[bold]Confidence:[/bold] {conf}\n"
        f"[bold]Cross-domain:[/bold] {cross_tags or 'none'}\n"
        f"[bold]Utility:[/bold] {utility_vector or 'none'}\n"
        f"[bold]Source:[/bold] {raw}\n"
        f"[bold]Epoch:[/bold] {epoch['id']}",
        title="[bold]Review Before Commit[/bold]",
        border_style="yellow"
    ))

    if not Confirm.ask("\nCommit this atom?"):
        console.print("[dim]Cancelled.[/dim]")
        return

    atom_id, is_new = db.insert_atom(
        claim=claim,
        claim_type=claim_type,
        domain=wiz['domain'],
        source_ids=[raw],
        epoch_id=epoch['id'],
        model_id="human",
        extracted_by=f"wiz_{wizard}",
        speculation_level=spec,
        confidence_score=conf,
        cross_domain_tags=cross_tags,
        extraction_parameters={"method": "manual", "prompt_version": "human"},
    )

    if is_new:
        console.print(f"\n[green]✓ Atom created[/green] — ID: [yellow]{atom_id}[/yellow]")
        console.print(f"[dim]Status: candidate (pending review)[/dim]")
    else:
        console.print(f"\n[yellow]⚠ Duplicate atom[/yellow] — already exists: [yellow]{atom_id}[/yellow]")

    console.print()

@atom.command('list')
@click.option('--domain', '-d', default=None, help='Filter by domain')
@click.option('--status', '-s', default=None,
              type=click.Choice(['candidate', 'accepted', 'rejected', 'superseded']),
              help='Filter by status')
@click.option('--limit', '-n', default=20, help='Number of results')
def atom_list(domain, status, limit):
    """List atoms with optional filters."""
    atoms = db.list_atoms(domain=domain, status=status, limit=limit)

    if not atoms:
        console.print("[dim]No atoms found.[/dim]")
        return

    console.print()
    t = Table(
        title=f"Atoms — {domain or 'all domains'} | {status or 'all statuses'}",
        box=box.SIMPLE, show_header=True, header_style="bold dim"
    )
    t.add_column("ID", style="dim", max_width=16)
    t.add_column("Claim", max_width=60)
    t.add_column("Type", max_width=16)
    t.add_column("Spec", justify="center")
    t.add_column("Conf", justify="center")
    t.add_column("Status")
    t.add_column("Domain", max_width=20)

    status_colors = {
        "candidate": "yellow",
        "accepted": "green",
        "rejected": "red",
        "superseded": "dim"
    }

    for a in atoms:
        sid = a['id'][-12:]
        color = status_colors.get(a['status'], 'white')
        t.add_row(
            f"...{sid}",
            a['claim'][:57] + "..." if len(a['claim']) > 60 else a['claim'],
            a['claim_type'],
            str(a['speculation_level']),
            f"{a['confidence_score']:.2f}",
            f"[{color}]{a['status']}[/{color}]",
            a['domain']
        )

    console.print(t)
    console.print(f"[dim]Showing {len(atoms)} of available atoms.[/dim]\n")

# ============================================================
# REVIEW
# ============================================================

@cli.command()
@click.option('--wizard', '-w', default=None, help='Filter by wizard domain')
@click.option('--domain', '-d', default=None, help='Filter by domain directly')
def review(wizard, domain):
    """Review candidate atoms — accept or reject interactively."""
    target_domain = domain
    if wizard and not domain:
        wiz = db.get_wizard(wizard)
        if wiz:
            target_domain = wiz['domain']

    atoms = db.list_atoms(domain=target_domain, status='candidate', limit=50)

    if not atoms:
        console.print(
            f"\n[green]✓ No candidate atoms pending review[/green]"
            + (f" for domain '{target_domain}'" if target_domain else "") + "\n"
        )
        return

    console.print(f"\n[bold]Review Queue[/bold] — {len(atoms)} candidate atom(s)\n")

    accepted = rejected = skipped = 0

    for i, a in enumerate(atoms, 1):
        console.print(Panel(
            f"[bold]{a['claim']}[/bold]\n\n"
            f"[dim]Type:[/dim]       {a['claim_type']}\n"
            f"[dim]Speculation:[/dim] {a['speculation_level']}/5\n"
            f"[dim]Confidence:[/dim]  {a['confidence_score']:.2f}\n"
            f"[dim]Domain:[/dim]      {a['domain']}\n"
            f"[dim]Cross-domain:[/dim] {a['cross_domain_tags']}\n"
            f"[dim]Source:[/dim]     {json.loads(a['source_ids'])[0] if a['source_ids'] else 'unknown'}\n"
            f"[dim]Epoch:[/dim]      {a['epoch_id']}\n"
            f"[dim]ID:[/dim]         {a['id']}",
            title=f"[bold]Atom {i}/{len(atoms)}[/bold]",
            border_style="cyan"
        ))

        action = Prompt.ask(
            "Decision",
            choices=["a", "r", "s", "q"],
            default="s"
        )
        # a=accept, r=reject, s=skip, q=quit

        if action == "q":
            break
        elif action == "a":
            db.accept_atom(a['id'], reviewer="human")
            console.print("[green]✓ Accepted[/green]\n")
            accepted += 1
        elif action == "r":
            reason = Prompt.ask("Rejection reason")
            db.reject_atom(a['id'], reason=reason, reviewer="human")
            console.print("[red]✗ Rejected[/red]\n")
            rejected += 1
        else:
            console.print("[dim]Skipped[/dim]\n")
            skipped += 1

    console.print(
        f"\n[bold]Session complete[/bold] — "
        f"[green]{accepted} accepted[/green] | "
        f"[red]{rejected} rejected[/red] | "
        f"[dim]{skipped} skipped[/dim]\n"
    )

    if accepted + rejected > 0:
        rate = accepted / (accepted + rejected) * 100
        console.print(f"[dim]Acceptance rate this session: {rate:.0f}%[/dim]")
        console.print(f"[dim](Calibration target: 30-60%)[/dim]\n")

# ============================================================
# PATTERN
# ============================================================

@cli.group()
def pattern():
    """Pattern management — create and list."""
    pass

@pattern.command('create')
@click.option('--wizard', '-w', required=True)
def pattern_create(wizard):
    """Create a new pattern from accepted atoms."""
    wiz = db.get_wizard(wizard)
    if not wiz:
        console.print(f"[red]Wizard '{wizard}' not found.[/red]")
        sys.exit(1)

    epoch = db.get_active_epoch(wiz['id'])

    # Show accepted atoms for this domain
    atoms = db.list_atoms(domain=wiz['domain'], status='accepted', limit=100)
    if not atoms:
        console.print(f"[yellow]No accepted atoms in domain '{wiz['domain']}' yet.[/yellow]")
        console.print("[dim]Run: ohara review to accept atoms first.[/dim]")
        return

    console.print(f"\n[bold]Create Pattern[/bold] — {wiz['domain']}\n")
    console.print(f"[dim]Accepted atoms available: {len(atoms)}[/dim]\n")

    # Show atoms
    for i, a in enumerate(atoms, 1):
        console.print(f"  [cyan]{i:2d}.[/cyan] [{a['claim_type']}] {a['claim'][:80]}")
        console.print(f"       [dim]conf={a['confidence_score']:.2f} spec={a['speculation_level']} id=...{a['id'][-8:]}[/dim]")

    console.print()

    # Select atoms
    console.print("[bold]Select constituent atoms[/bold]")
    console.print("[dim]Enter comma-separated numbers from the list above[/dim]")
    while True:
        selection = Prompt.ask("Atoms")
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(",")]
            selected = [atoms[i] for i in indices if 0 <= i < len(atoms)]
            if len(selected) < 2:
                console.print("[yellow]Select at least 2 atoms.[/yellow]")
            else:
                break
        except (ValueError, IndexError):
            console.print("[red]Invalid selection.[/red]")

    console.print(f"\n[dim]Selected {len(selected)} atoms.[/dim]")

    # Title
    console.print("\n[bold]Pattern title[/bold] [dim](max 120 chars)[/dim]")
    while True:
        title = Prompt.ask("Title")
        if len(title) > 120:
            console.print("[red]Too long.[/red]")
        elif len(title) < 10:
            console.print("[yellow]Too short. Be specific.[/yellow]")
        else:
            break

    # Summary
    console.print("\n[bold]Pattern summary[/bold] [dim](max 500 chars — what structural claim does this cluster represent?)[/dim]")
    while True:
        summary = Prompt.ask("Summary")
        if len(summary) > 500:
            console.print("[red]Too long.[/red]")
        elif len(summary) < 30:
            console.print("[yellow]Too short. Explain the pattern properly.[/yellow]")
        else:
            break

    # Compute fields
    atom_ids_list = [a['id'] for a in selected]
    all_source_ids = []
    for a in selected:
        all_source_ids.extend(json.loads(a['source_ids']))
    src_hash = db.source_hash_set(list(set(all_source_ids)))
    pat_id = "pat_" + db.ulid()[:16]

    console.print()
    console.print(Panel(
        f"[bold]Title:[/bold] {title}\n"
        f"[bold]Summary:[/bold] {summary}\n"
        f"[bold]Atoms:[/bold] {len(selected)}\n"
        f"[bold]Domain:[/bold] {wiz['domain']}\n"
        f"[bold]Status:[/bold] signal (initial)",
        title="[bold]Review Pattern[/bold]",
        border_style="yellow"
    ))

    if not Confirm.ask("\nCreate this pattern?"):
        console.print("[dim]Cancelled.[/dim]")
        return

    conn = db.knowledge_db()
    try:
        conn.execute("""
            INSERT INTO patterns (
                id, title, summary, domain, status, status_changed_at,
                atom_ids, atom_count, source_hash_set, epoch_id, version,
                created_by, updated_by
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            pat_id, title, summary, wiz['domain'],
            'signal', db.now(),
            json.dumps(atom_ids_list), len(atom_ids_list),
            src_hash, epoch['id'], 1,
            f"wiz_{wizard}", f"wiz_{wizard}"
        ))
        # Write history
        conn.execute("""
            INSERT INTO pattern_history (
                id, pattern_id, version, status_from, status_to,
                changed_at, changed_by, epoch_id, rationale
            ) VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            db.ulid("ph_"), pat_id, 1, "created", "signal",
            db.now(), f"wiz_{wizard}", epoch['id'],
            "Initial pattern creation from manual calibration."
        ))
        conn.commit()
    finally:
        conn.close()

    console.print(f"\n[green]✓ Pattern created[/green] — ID: [yellow]{pat_id}[/yellow]")
    console.print(f"[dim]Status: signal[/dim]\n")

@pattern.command('list')
@click.option('--domain', '-d', default=None)
@click.option('--status', '-s', default=None)
def pattern_list(domain, status):
    """List patterns."""
    patterns = db.list_patterns(domain=domain, status=status)
    if not patterns:
        console.print("[dim]No patterns found.[/dim]")
        return

    console.print()
    t = Table(title="Patterns", box=box.SIMPLE, header_style="bold dim")
    t.add_column("ID", style="dim", max_width=14)
    t.add_column("Title", max_width=45)
    t.add_column("Domain", max_width=22)
    t.add_column("Status")
    t.add_column("Atoms", justify="center")
    t.add_column("CE", justify="center")

    colors = {
        "signal": "dim", "emerging": "yellow", "validated": "green",
        "structural": "bold green", "deprecated": "red"
    }
    for p in patterns:
        color = colors.get(p['status'], 'white')
        t.add_row(
            f"...{p['id'][-10:]}",
            p['title'][:42] + "..." if len(p['title']) > 45 else p['title'],
            p['domain'],
            f"[{color}]{p['status']}[/{color}]",
            str(p['atom_count']),
            str(p['counter_evidence_count'])
        )
    console.print(t)
    console.print()

# ============================================================
# GOD COMMANDS
# ============================================================

@cli.group()
def god():
    """God-mode commands — overseer interface."""
    pass

@god.command('digest')
def god_digest():
    """Daily digest — what happened, what needs your attention."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]GOD DIGEST[/bold cyan]\n[dim]What needs your attention[/dim]",
        border_style="cyan"
    ))

    stats = db.library_stats()

    # Library health
    console.print("\n[bold]Library State[/bold]")
    t = Table(box=box.SIMPLE, show_header=False)
    t.add_column("", style="dim")
    t.add_column("", style="bold")
    t.add_row("Raw items", str(stats['raw_items_total']))
    t.add_row("Atoms accepted", str(stats.get('atoms_accepted', 0)))
    t.add_row("Atoms pending", str(stats.get('atoms_candidate', 0)))
    t.add_row("Books", str(stats['books_total']))
    console.print(t)

    # Patterns by status
    by_status = stats.get('patterns_by_status', {})
    if by_status:
        console.print("\n[bold]Patterns[/bold]")
        t2 = Table(box=box.SIMPLE, show_header=False)
        t2.add_column("", style="dim")
        t2.add_column("", style="bold")
        colors = {
            "signal": "dim", "emerging": "yellow", "validated": "green",
            "structural": "bold green", "deprecated": "red"
        }
        for s, count in by_status.items():
            color = colors.get(s, 'white')
            t2.add_row(f"  {s}", f"[{color}]{count}[/{color}]")
        console.print(t2)

    # Patterns awaiting STRUCTURAL approval
    conn = db.knowledge_db()
    validated = conn.execute(
        "SELECT id, title, domain, status_changed_at FROM patterns WHERE status='validated'"
    ).fetchall()
    conn.close()

    if validated:
        console.print(f"\n[bold yellow]⚑ Patterns awaiting STRUCTURAL review ({len(validated)})[/bold yellow]")
        console.print("[dim]These are in your queue. Use: ohara god approve --pattern <id>[/dim]")
        for p in validated:
            console.print(f"  [yellow]→[/yellow] {p['title'][:60]} [dim]({p['domain']}, since {p['status_changed_at'][:10]})[/dim]")
    else:
        console.print("\n[dim]No patterns awaiting STRUCTURAL approval.[/dim]")

    # Unresolved counter-evidence
    if stats['counter_evidence_unresolved'] > 0:
        console.print(f"\n[bold red]⚠ Unresolved counter-evidence: {stats['counter_evidence_unresolved']}[/bold red]")
        console.print("[dim]Run: ohara god ce-review[/dim]")

    # Pending atoms
    if stats.get('atoms_candidate', 0) > 0:
        console.print(f"\n[yellow]⚑ {stats['atoms_candidate']} atom(s) pending review[/yellow]")
        console.print("[dim]Run: ohara review[/dim]")

    console.print()

@god.command('approve')
@click.option('--pattern', '-p', required=True, help='Pattern ID to promote to STRUCTURAL')
@click.option('--rationale', '-r', default=None, help='Approval rationale (min 100 chars)')
def god_approve(pattern, rationale):
    """Promote a VALIDATED pattern to STRUCTURAL. God-only action."""
    conn = db.knowledge_db()
    try:
        row = conn.execute("SELECT * FROM patterns WHERE id=?", (pattern,)).fetchone()
        if not row:
            console.print(f"[red]Pattern '{pattern}' not found.[/red]")
            return

        p = dict(row)
        if p['status'] != 'validated':
            console.print(f"[red]Pattern must be in 'validated' status. Current: {p['status']}[/red]")
            return

        if p['unresolved_strong_count'] > 0:
            console.print(f"[red]BLOCKED: {p['unresolved_strong_count']} unresolved strong counter-evidence.[/red]")
            console.print("[dim]Resolve all strong/fatal counter-evidence before STRUCTURAL promotion.[/dim]")
            return

        console.print()
        console.print(Panel(
            f"[bold]{p['title']}[/bold]\n\n"
            f"{p['summary']}\n\n"
            f"[dim]Domain:[/dim] {p['domain']}\n"
            f"[dim]Atoms:[/dim] {p['atom_count']}\n"
            f"[dim]Confidence avg:[/dim] {p['confidence_score_avg'] or 'N/A'}\n"
            f"[dim]Counter-evidence:[/dim] {p['counter_evidence_count']} total, {p['unresolved_strong_count']} unresolved strong",
            title="[bold yellow]STRUCTURAL Promotion Review[/bold yellow]",
            border_style="yellow"
        ))

        if not rationale:
            console.print("\n[bold]Approval rationale required[/bold] [dim](min 100 characters)[/dim]")
            while True:
                rationale = Prompt.ask("Rationale")
                if len(rationale) >= 100:
                    break
                console.print(f"[red]Too short ({len(rationale)} chars). Min 100.[/red]")

        console.print(f"\n[bold red]⚠ WARNING: STRUCTURAL promotion is permanent (requires /REPLAN to undo)[/bold red]")
        if not Confirm.ask("Confirm STRUCTURAL promotion?"):
            console.print("[dim]Cancelled.[/dim]")
            return

        epoch = db.get_active_epoch()
        conn.execute("""
            UPDATE patterns SET
                status='structural',
                structural_approved_by='op_god_001',
                structural_approved_at=?,
                structural_rationale=?,
                status_changed_at=?,
                updated_at=?,
                updated_by='op_god_001',
                version=version+1
            WHERE id=?
        """, (db.now(), rationale, db.now(), db.now(), pattern))

        conn.execute("""
            INSERT INTO pattern_history (
                id, pattern_id, version, status_from, status_to,
                changed_at, changed_by, epoch_id, rationale
            ) VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            db.ulid("ph_"), pattern, p['version'] + 1,
            'validated', 'structural',
            db.now(), 'op_god_001', epoch['id'], rationale
        ))
        conn.commit()

        console.print(f"\n[bold green]✓ STRUCTURAL promotion approved[/bold green]")
        console.print(f"[dim]Pattern '{p['title']}' is now STRUCTURAL knowledge.[/dim]\n")

    finally:
        conn.close()

@god.command('redirect')
@click.option('--wizard', '-w', required=True, help='Wizard to redirect')
@click.option('--instruction', '-i', required=True, help='Instruction for the wizard')
def god_redirect(wizard, instruction):
    """Send a governance instruction to a wizard."""
    wiz = db.get_wizard(wizard)
    if not wiz:
        console.print(f"[red]Wizard '{wizard}' not found.[/red]")
        return

    console.print(f"\n[bold]Redirect: {wiz['name']}[/bold]")
    console.print(f"[dim]Instruction:[/dim] {instruction}")

    if not Confirm.ask("\nConfirm redirect?"):
        console.print("[dim]Cancelled.[/dim]")
        return

    conn = db.governance_db()
    try:
        conn.execute("""
            INSERT INTO governance_actions (
                id, action_type, wizard_id, triggered_by, triggered_at,
                god_instruction, status
            ) VALUES (?,?,?,?,?,?,?)
        """, (
            db.ulid("gov_"), 'god_redirect', wiz['id'],
            'god', db.now(), instruction, 'open'
        ))
        conn.commit()
    finally:
        conn.close()

    console.print(f"\n[green]✓ Redirect logged[/green] for {wiz['name']}\n")

# ============================================================
# WIZARDS
# ============================================================

@cli.command()
def wizards():
    """List all wizards and their status."""
    all_wizards = db.list_active_wizards()
    console.print()
    for w in all_wizards:
        collabs = json.loads(w.get('known_collaborators', '[]'))
        console.print(Panel(
            f"[bold]{w['name']}[/bold] [dim]({w['short_name']})[/dim]\n\n"
            f"[dim]Domain:[/dim]    {w['domain']}\n"
            f"[dim]Specialty:[/dim] {w['specialty']}\n\n"
            f"[dim italic]{w['persona_summary']}[/dim italic]\n\n"
            f"[dim]Collaborators:[/dim] {', '.join(collabs) or 'none yet'}",
            border_style="cyan",
            width=80
        ))
    console.print()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    cli()
