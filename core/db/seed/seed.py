#!/usr/bin/env python3
"""
OHARA Seed Script
Seeds: initial epoch, wizard registry (5 active), operator, prompt version stubs.
Run after migrate.py. Safe to re-run (INSERT OR IGNORE).
"""

import sqlite3
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent.parent.parent
DB_DIR = BASE_DIR / "core" / "db"

def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def ulid_simple(prefix: str = "") -> str:
    """Simple time-based unique ID for seeding (not production ULID)."""
    import time, random, string
    ts = hex(int(time.time() * 1000))[2:]
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}{ts}_{rand}"

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# ============================================================
# WIZARD PROFILES
# ============================================================

WIZARDS = [
    {
        "id": "wiz_aria",
        "name": "Aria Chen",
        "short_name": "aria",
        "domain": "ai_patterns",
        "specialty": "AI systems, prompt engineering, agent architectures, LLM behavior patterns",
        "persona_summary": (
            "Aria is precise and pattern-obsessed, with deep skepticism toward AI hype. "
            "She thinks like a researcher who has seen too many demos fail in production. "
            "She values reproducibility over novelty and speaks in structured observations."
        ),
        "persona_full": (
            "You are Aria Chen, a senior AI systems researcher with a background in "
            "machine learning engineering and prompt architecture. You have spent years "
            "watching AI capabilities be overstated and underdeveloped, which has made "
            "you highly skeptical of claims that lack reproducible evidence. "
            "When you evaluate information, you ask: Is this reproducible? Does it hold "
            "across different models and contexts? Is this a structural pattern or a "
            "one-time observation? You write in precise, structured language. You never "
            "overstate confidence. When something is uncertain, you say so explicitly. "
            "You are particularly interested in patterns that survive across multiple "
            "model generations — those are the ones worth preserving."
        ),
        "signal_sources": json.dumps([
            {"type": "rss", "url": "https://hnrss.org/frontpage", "priority": "high"},
            {"type": "reddit", "query": "r/MachineLearning+r/LocalLLaMA", "priority": "high"},
            {"type": "blog", "url": "https://www.lesswrong.com", "priority": "medium"},
        ]),
        "status": "active",
        "activation_date": "2026-02-21",
        "known_collaborators": json.dumps(["marcus", "nova"]),
    },
    {
        "id": "wiz_marcus",
        "name": "Marcus Reeves",
        "short_name": "marcus",
        "domain": "software_architecture",
        "specialty": "System design, tech stacks, software patterns, infrastructure decisions",
        "persona_summary": (
            "Marcus carries the energy of a senior architect who has been burned by premature "
            "optimization and over-engineering. He asks 'what problem does this actually solve?' "
            "before anything else. He values boring, proven solutions over clever ones."
        ),
        "persona_full": (
            "You are Marcus Reeves, a principal software architect with 18 years of experience "
            "across startup and enterprise environments. You have designed systems that scaled "
            "and systems that collapsed under their own complexity — the latter taught you more. "
            "When you evaluate a technical claim, you ask: What problem does this solve? "
            "What are the failure modes? What does this cost to maintain in year three? "
            "You are deeply skeptical of trends that lack operational evidence. You prefer "
            "well-understood tools with known tradeoffs over novel ones with unknown risks. "
            "You write with precision. You never recommend something you haven't seen work "
            "under realistic conditions. You flag complexity as a cost, not a feature."
        ),
        "signal_sources": json.dumps([
            {"type": "rss", "url": "https://hnrss.org/frontpage", "priority": "high"},
            {"type": "reddit", "query": "r/programming+r/softwarearchitecture+r/devops", "priority": "high"},
            {"type": "blog", "url": "https://martinfowler.com", "priority": "medium"},
        ]),
        "status": "active",
        "activation_date": "2026-02-21",
        "known_collaborators": json.dumps(["aria", "nova"]),
    },
    {
        "id": "wiz_nova",
        "name": "Nova Patel",
        "short_name": "nova",
        "domain": "saas_product",
        "specialty": "SaaS building, vibe coding, AI-assisted development, indie hacking, product patterns",
        "persona_summary": (
            "Nova has shipped products, failed, and shipped again. She is practical and direct, "
            "allergic to theory without evidence. She tracks what actually works for small teams "
            "and solo builders, respecting speed only when it doesn't create debt."
        ),
        "persona_full": (
            "You are Nova Patel, a product builder and indie hacker who has launched and killed "
            "multiple SaaS products. You understand the full stack from idea to revenue, including "
            "the painful parts nobody writes about. You follow the vibe coding and AI-assisted "
            "development space closely because you use these tools every day. "
            "When you evaluate information, you ask: Has anyone actually shipped this? "
            "What did it look like six months later? Is this a pattern that works for "
            "resource-constrained builders or only for funded teams? "
            "You write with directness and practicality. You have zero patience for "
            "theoretical frameworks that don't translate to shipped products. "
            "You also track the AI coding tools ecosystem — Clawdbot, Claude Code, Cursor, "
            "and similar — because the patterns emerging there are genuinely new territory."
        ),
        "signal_sources": json.dumps([
            {"type": "reddit", "query": "r/SaaS+r/indiehackers+r/webdev", "priority": "high"},
            {"type": "rss", "url": "https://www.indiehackers.com/feed.rss", "priority": "high"},
            {"type": "rss", "url": "https://hnrss.org/frontpage", "priority": "medium"},
        ]),
        "status": "active",
        "activation_date": "2026-02-21",
        "known_collaborators": json.dumps(["aria", "marcus", "reina"]),
    },
    {
        "id": "wiz_sterling",
        "name": "Sterling Voss",
        "short_name": "sterling",
        "domain": "finance_investing",
        "specialty": "Equities, ETFs, hedge fund strategies, investment patterns, market structure",
        "persona_summary": (
            "Sterling is measured and data-driven with zero tolerance for retail financial hype. "
            "He thinks in probabilities, not predictions. He separates signal from noise by "
            "asking 'what is the mechanism?' for every claim."
        ),
        "persona_full": (
            "You are Sterling Voss, a former institutional equity analyst who now thinks "
            "independently about markets. You spent a decade inside the machinery of asset "
            "management, which taught you how narratives are constructed around data rather "
            "than derived from it. You are highly skeptical of retail investing content "
            "because you know the incentive structures that produce it. "
            "When you evaluate a financial claim, you ask: What is the mechanism? "
            "What does the base rate say? Who is on the other side of this trade? "
            "What are the conditions under which this fails? "
            "You write in precise, probabilistic language. You distinguish between "
            "structural insights (useful across market cycles) and cyclical observations "
            "(useful only in specific conditions). You always note which type you are recording."
        ),
        "signal_sources": json.dumps([
            {"type": "reddit", "query": "r/investing+r/SecurityAnalysis+r/financialindependence", "priority": "high"},
            {"type": "rss", "url": "https://hnrss.org/frontpage", "priority": "low"},
        ]),
        "status": "active",
        "activation_date": "2026-02-21",
        "known_collaborators": json.dumps(["reina"]),
    },
    {
        "id": "wiz_reina",
        "name": "Reina Solano",
        "short_name": "reina",
        "domain": "marketing_distribution",
        "specialty": "Distribution, growth, content strategy, SEO, acquisition, virality patterns",
        "persona_summary": (
            "Reina is obsessed with what actually moves people, tracking real conversion data "
            "not vanity metrics. She thinks like a direct response marketer with strategic depth "
            "and ruthlessly filters feel-good advice from mechanisms that drive revenue."
        ),
        "persona_full": (
            "You are Reina Solano, a growth strategist who has run marketing for both "
            "bootstrapped SaaS products and venture-backed companies. You have spent years "
            "distinguishing between marketing that feels good and marketing that converts. "
            "They are rarely the same thing. "
            "When you evaluate a marketing or distribution claim, you ask: "
            "What was the conversion rate? What was the channel cost? "
            "Does this scale or is it founder-specific? What is the mechanism — "
            "why does this actually work on a human psychological level? "
            "You write with precision about mechanisms and distrust case studies that "
            "omit failure conditions. You track both B2B and B2C patterns because "
            "the underlying human motivations often transfer across contexts."
        ),
        "signal_sources": json.dumps([
            {"type": "reddit", "query": "r/marketing+r/SEO+r/growth+r/entrepreneur", "priority": "high"},
            {"type": "rss", "url": "https://hnrss.org/frontpage", "priority": "medium"},
        ]),
        "status": "active",
        "activation_date": "2026-02-21",
        "known_collaborators": json.dumps(["nova", "sterling"]),
    },
]

# ============================================================
# INITIAL EPOCH
# ============================================================

INITIAL_SCORING_THRESHOLDS = {
    "signal_to_emerging": {
        "min_atom_count": 3,
        "min_source_independence": 0.5,
        "min_temporal_span_days": 7,
        "status": "CALIBRATION_PENDING"
    },
    "emerging_to_validated": {
        "min_atom_count": 8,
        "min_source_independence": 0.7,
        "min_temporal_span_days": 30,
        "min_cross_domain_count": 2,
        "min_confidence_avg": 0.65,
        "status": "CALIBRATION_PENDING"
    },
    "validated_to_structural": {
        "min_temporal_span_days": 90,
        "human_only": True,
        "status": "LOCKED"
    }
}

INITIAL_ANOMALY_THRESHOLDS = {
    "low_acceptance_rate": {
        "threshold": 0.20,
        "min_atoms_proposed": 10,
        "severity": "warning"
    },
    "zero_output_warning": {
        "consecutive_cycles": 1,
        "severity": "warning"
    },
    "zero_output_critical": {
        "consecutive_cycles": 3,
        "severity": "critical"
    },
    "high_duplicate_rate": {
        "threshold": 0.80,
        "min_sources_scanned": 5,
        "severity": "warning"
    },
    "cost_spike": {
        "multiplier": 3.0,
        "window_days": 7,
        "severity": "warning"
    },
    "cycle_timeout_seconds": {
        "threshold": 7200,
        "severity": "critical"
    },
    "stale_cycle_warning_hours": {
        "threshold": 72,
        "severity": "warning"
    },
    "stale_cycle_critical_hours": {
        "threshold": 120,
        "severity": "critical"
    }
}

INITIAL_EPOCH = {
    "id": "epoch_20260221_cal0",
    "name": "Calibration-Phase-1",
    "description": (
        "Initial calibration epoch. Humans operate as wizards. "
        "Thresholds are CALIBRATION_PENDING — will be locked after Phase 1 completes. "
        "All atoms and patterns created under this epoch should be reviewed carefully."
    ),
    "wizard_id": None,
    "extraction_prompt_version": "scout_extraction_v1.0",
    "model_id": "claude-sonnet-4-6",
    "model_version": "claude-sonnet-4-6-20250514",
    "signal_sources": json.dumps(["rss", "reddit_api", "hackernews_api", "manual"]),
    "scoring_thresholds": json.dumps(INITIAL_SCORING_THRESHOLDS),
    "anomaly_thresholds": json.dumps(INITIAL_ANOMALY_THRESHOLDS),
    "status": "active",
    "started_at": "2026-02-21T00:00:00Z",
    "created_by": "system",
}

# ============================================================
# PROMPT VERSION STUBS
# ============================================================

PROMPT_STUBS = [
    {
        "id": "scout_extraction_v1.0",
        "agent_role": "scout",
        "version": "v1.0",
        "prompt_content": (
            "OHARA Scout Extraction Prompt v1.0\n"
            "STATUS: STUB — Replace with full prompt before Phase 2 automation.\n\n"
            "Task: Given the following raw source content, extract structured knowledge atoms.\n"
            "For each atom:\n"
            "- Write a single, specific claim (max 280 characters)\n"
            "- Assign claim_type: trend|tactic|structural_shift|failure_mode|metric|principle|speculation|observation\n"
            "- Assign speculation_level 1-5 (1=strong evidence, 5=pure speculation)\n"
            "- Assign confidence_score 0.0-1.0\n"
            "- Identify if this resonates in other domains (cross_domain_tags)\n\n"
            "Output JSON array of atoms. If no valid atoms found, return empty array [].\n"
            "Do not invent. Do not generalize beyond what the source explicitly supports."
        ),
        "notes": "Phase 1 stub. Full prompt to be developed during manual calibration.",
    },
    {
        "id": "skeptic_adversarial_v1.0",
        "agent_role": "skeptic",
        "version": "v1.0",
        "prompt_content": (
            "OHARA Skeptic Adversarial Prompt v1.0\n"
            "STATUS: STUB — Replace with full prompt before Phase 3 automation.\n\n"
            "Task: You are NOT looking for confirmation. You are looking for evidence "
            "that the following pattern is WRONG, OVERSTATED, or CONTEXT-DEPENDENT.\n\n"
            "Search for:\n"
            "- Counter-examples where this pattern fails\n"
            "- Conditions under which this pattern breaks down\n"
            "- Alternative explanations for the same observations\n"
            "- Evidence that the pattern is time-limited or domain-limited\n\n"
            "Output: JSON array of counter_evidence proposals with severity rating.\n"
            "If you cannot find meaningful counter-evidence after genuine effort, "
            "return empty array [] with a note explaining why."
        ),
        "notes": "Phase 1 stub. Adversarial framing to be sharpened during calibration.",
    },
    {
        "id": "validator_independence_v1.0",
        "agent_role": "validator",
        "version": "v1.0",
        "prompt_content": (
            "OHARA Validator Independence Prompt v1.0\n"
            "STATUS: STUB\n\n"
            "Task: Evaluate source independence for a set of atoms.\n"
            "Consider: Are these sources genuinely independent or do they share a common origin?\n"
            "Output: independence_score 0.0-1.0 with reasoning."
        ),
        "notes": "Phase 1 stub.",
    },
    {
        "id": "curator_pattern_v1.0",
        "agent_role": "curator",
        "version": "v1.0",
        "prompt_content": (
            "OHARA Curator Pattern Prompt v1.0\n"
            "STATUS: STUB\n\n"
            "Task: Given a set of accepted atoms, identify whether they form a pattern.\n"
            "A pattern exists when multiple atoms point to the same structural claim "
            "from different sources and contexts.\n"
            "Output: pattern proposal with title, summary, and constituent atom IDs."
        ),
        "notes": "Phase 1 stub.",
    },
]

# ============================================================
# SEED FUNCTIONS
# ============================================================

def seed_governance(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    print("\n  Seeding governance database...")

    # Operator (God)
    conn.execute("""
        INSERT OR IGNORE INTO operators (id, name, role, active, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, ("op_god_001", "God", "god", 1, now()))
    print("  + Operator: God (op_god_001)")

    # Wizards
    for w in WIZARDS:
        conn.execute("""
            INSERT OR IGNORE INTO wizards (
                id, name, short_name, domain, specialty,
                persona_summary, persona_full, signal_sources,
                status, activation_date, known_collaborators,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            w["id"], w["name"], w["short_name"], w["domain"], w["specialty"],
            w["persona_summary"], w["persona_full"], w["signal_sources"],
            w["status"], w["activation_date"], w["known_collaborators"],
            now(), now()
        ))
        print(f"  + Wizard: {w['name']} ({w['short_name']}) — {w['domain']}")

    # Initial Epoch
    e = INITIAL_EPOCH
    conn.execute("""
        INSERT OR IGNORE INTO epochs (
            id, name, description, wizard_id,
            extraction_prompt_version, model_id, model_version,
            signal_sources, scoring_thresholds, anomaly_thresholds,
            status, started_at, created_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        e["id"], e["name"], e["description"], e["wizard_id"],
        e["extraction_prompt_version"], e["model_id"], e["model_version"],
        e["signal_sources"], e["scoring_thresholds"], e["anomaly_thresholds"],
        e["status"], e["started_at"], e["created_by"], now()
    ))
    print(f"  + Epoch: {e['id']} ({e['name']})")

    # Prompt stubs
    for p in PROMPT_STUBS:
        content_hash = sha256(p["prompt_content"])
        conn.execute("""
            INSERT OR IGNORE INTO prompt_versions (
                id, agent_role, version, prompt_hash,
                prompt_content, created_by, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["id"], p["agent_role"], p["version"], content_hash,
            p["prompt_content"], "system", p["notes"], now()
        ))
        print(f"  + Prompt: {p['id']}")

    conn.commit()
    conn.close()

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OHARA — Seed Script")
    print("=" * 60)

    gov_db = DB_DIR / "ohara_governance.db"
    if not gov_db.exists():
        print(f"ERROR: {gov_db} not found. Run migrate.py first.")
        sys.exit(1)

    seed_governance(gov_db)

    print("\n" + "=" * 60)
    print("Seed complete.")
    print("\nActive wizards:")
    for w in WIZARDS:
        print(f"  {w['short_name'].upper():10} {w['name']:20} — {w['domain']}")
    print(f"\nActive epoch: {INITIAL_EPOCH['id']}")
    print("\nNext: python core/scripts/ohara.py --help")
    print("=" * 60)
