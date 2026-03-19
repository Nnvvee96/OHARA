"""
OHARA — Scout Agent
Fetches sources from a wizard's signal perimeter,
extracts candidate atoms using LLM with wizard persona injected.

One scout instance per wizard domain.
Emits vitality record on every cycle completion.
"""

import json
import time
import urllib.request
import urllib.error
import os
import sys
import html
import re
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

import db
import llm

MAX_SOURCES   = int(os.getenv("SCOUT_MAX_SOURCES_PER_CYCLE", "10"))
MAX_ATOMS     = int(os.getenv("SCOUT_MAX_ATOMS_PER_SOURCE", "5"))
FETCH_DELAY   = float(os.getenv("SCOUT_CYCLE_DELAY_SECONDS", "3"))
MAX_CONTENT   = 6000  # chars sent to LLM — keeps tokens bounded

# ============================================================
# SOURCE FETCHERS
# ============================================================

def fetch_hackernews_top(limit: int = 15) -> list[dict]:
    """Fetch top HackerNews stories — free, no auth."""
    try:
        with urllib.request.urlopen(
            "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10
        ) as r:
            ids = json.loads(r.read())[:limit]

        stories = []
        for sid in ids:
            try:
                with urllib.request.urlopen(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=8
                ) as r:
                    item = json.loads(r.read())
                if item and item.get("type") == "story" and item.get("url"):
                    stories.append({
                        "url": item["url"],
                        "title": item.get("title", ""),
                        "source": "hackernews",
                        "tier": "aggregator",
                        "independence": 0.6,
                        "text": item.get("title", "") + "\n" + item.get("text", ""),
                    })
                time.sleep(0.2)
            except Exception:
                continue
        return stories
    except Exception as e:
        print(f"  [HN] Fetch failed: {e}")
        return []

def fetch_reddit(subreddits: str, limit: int = 15) -> list[dict]:
    """Fetch Reddit hot posts — free JSON API."""
    results = []
    for sub in subreddits.split("+"):
        sub = sub.strip().lstrip("r/")
        try:
            req = urllib.request.Request(
                f"https://www.reddit.com/r/{sub}/hot.json?limit={limit}",
                headers={"User-Agent": "OHARA/1.0 knowledge-librarian"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            posts = data.get("data", {}).get("children", [])
            for p in posts:
                d = p.get("data", {})
                if d.get("is_self") and d.get("selftext"):
                    content = d.get("title", "") + "\n\n" + d.get("selftext", "")
                else:
                    content = d.get("title", "")
                if len(content) < 50:
                    continue
                results.append({
                    "url": f"https://reddit.com{d.get('permalink', '')}",
                    "title": d.get("title", ""),
                    "source": f"reddit/r/{sub}",
                    "tier": "social",
                    "independence": 0.4,
                    "text": content,
                })
            time.sleep(FETCH_DELAY)
        except Exception as e:
            print(f"  [Reddit/{sub}] Fetch failed: {e}")
    return results

def fetch_url_content(url: str) -> tuple[bytes, str]:
    """Fetch raw content from URL."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "OHARA/1.0 knowledge-librarian"}
    )
    with urllib.request.urlopen(req, timeout=12) as r:
        content = r.read()
        ct = r.headers.get("Content-Type", "text/html")
    return content, ct

def clean_html(raw: bytes) -> str:
    """Extract readable text from HTML — minimal, no deps."""
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_CONTENT]

# ============================================================
# EXTRACTION PROMPT
# ============================================================

EXTRACTION_PROMPT = """You are {wizard_name}, operating as a knowledge wizard for OHARA — a rigorous epistemic library.

Your identity:
{persona_summary}

Your domain: {domain}

TASK: Analyze the following content and extract structured knowledge atoms.

WHAT IS A KNOWLEDGE ATOM:
- A single, specific, falsifiable claim
- Something a genuine expert would find non-obvious and useful
- Something that holds true beyond the moment it was written
- NOT a summary, NOT a headline, NOT an opinion without mechanism

WHAT IS NOT AN ATOM:
- Vague generalities ("AI is changing everything")
- Pure hype without mechanism
- Things everyone already knows
- Single data points without structural significance

SOURCE:
URL: {url}
---
{content}
---

Extract 0 to {max_atoms} atoms from this source. If there is nothing genuinely worth preserving, return an empty array.

For each atom, return:
- claim: string, max 280 chars, single specific claim
- claim_type: one of [trend, tactic, structural_shift, failure_mode, metric, principle, speculation, observation]
- speculation_level: integer 1-5 (1=strong evidence, 5=pure speculation)
- confidence_score: float 0.0-1.0
- cross_domain_tags: array of domains this resonates in (from: ai_patterns, software_architecture, saas_product, finance_investing, marketing_distribution) — exclude your own domain
- utility_vector: array of potential utility types — include ALL that apply, even speculatively:
    "product_building"    → could lead to building a product, app, SaaS, tool
    "process_improvement" → improves or automates a process
    "system_enhancement"  → enhances or replaces a system component
    "financial"           → applicable to trading, investing, revenue
    "future_optionality"  → no clear use now but worth preserving
    "personal_capability" → improves skills, judgment, knowledge
    "creative_enabling"   → enables new forms of creation
    "decision_support"    → helps make better decisions
  If no utility type applies even speculatively → do NOT include this atom. It is noise.
- reasoning: one sentence explaining why this is worth preserving

Respond with ONLY a JSON array. No preamble. No explanation outside the JSON.
If nothing is worth extracting, respond with: []

Example format:
[
  {{
    "claim": "Specific falsifiable claim under 280 chars",
    "claim_type": "principle",
    "speculation_level": 2,
    "confidence_score": 0.75,
    "cross_domain_tags": ["software_architecture"],
    "reasoning": "This pattern appears repeatedly across multiple independent sources."
  }}
]"""

# ============================================================
# MAIN SCOUT CYCLE
# ============================================================

def run_cycle(wizard_short_name: str, verbose: bool = True) -> dict:
    """
    Run one full scout cycle for a wizard.
    Returns vitality record dict.
    """
    wiz = db.get_wizard(wizard_short_name)
    if not wiz:
        raise ValueError(f"Wizard '{wizard_short_name}' not found or inactive.")

    epoch = db.get_active_epoch(wiz['id'])
    cycle_id = db.ulid("cvit_")
    started_at = db.now()

    if verbose:
        print(f"\n{'='*60}")
        print(f"SCOUT CYCLE — {wiz['name']} ({wiz['domain']})")
        print(f"Epoch: {epoch['id']}")
        print(f"Model: {llm.model_info()['extraction_model']}")
        print(f"{'='*60}")

    # Vitality counters
    sources_scanned = 0
    raw_ingested = 0
    raw_duplicate = 0
    atoms_proposed = 0
    atoms_written = 0
    atoms_duplicate = 0
    errors = []

    # Build source list from wizard config
    signal_sources = json.loads(wiz['signal_sources'])
    sources_to_fetch = []

    for src in signal_sources[:MAX_SOURCES]:
        src_type = src.get("type", "")
        if src_type == "rss" and "hackernews" in src.get("url", ""):
            items = fetch_hackernews_top(limit=8)
            sources_to_fetch.extend(items)
        elif src_type == "reddit":
            query = src.get("query", "")
            items = fetch_reddit(query, limit=8)
            sources_to_fetch.extend(items)

    if verbose:
        print(f"\nSources fetched: {len(sources_to_fetch)}")

    # Process each source
    for src in sources_to_fetch[:MAX_SOURCES]:
        sources_scanned += 1
        url = src["url"]
        tier = src.get("tier", "secondary")
        independence = src.get("independence", 0.5)

        if verbose:
            print(f"\n  [{sources_scanned}] {url[:70]}")

        # Get content — use pre-fetched text if available, else fetch URL
        if src.get("text"):
            content_text = src["text"][:MAX_CONTENT]
            content_bytes = content_text.encode("utf-8")
            ctype = "text"
        else:
            try:
                content_bytes, ct_header = fetch_url_content(url)
                content_text = clean_html(content_bytes)[:MAX_CONTENT]
                ctype = "html"
                time.sleep(FETCH_DELAY)
            except Exception as e:
                if verbose:
                    print(f"       Fetch error: {e}")
                errors.append(str(e))
                continue

        # Ingest to vault
        raw_id, is_new = db.insert_raw_item(
            origin_url=url,
            domain=wiz['domain'],
            content=content_bytes,
            content_type=ctype,
            source_tier=tier,
            ingestion_agent=f"scout_{wizard_short_name}",
            epoch_id=epoch['id'],
            editorial_independence=independence,
        )

        if not is_new:
            raw_duplicate += 1
            if verbose:
                print(f"       [dup] Already in vault")
            continue

        raw_ingested += 1

        if len(content_text) < 100:
            if verbose:
                print(f"       [skip] Content too short")
            continue

        # Build extraction prompt with wizard persona
        prompt = EXTRACTION_PROMPT.format(
            wizard_name=wiz['name'],
            persona_summary=wiz['persona_summary'],
            domain=wiz['domain'],
            url=url,
            content=content_text,
            max_atoms=MAX_ATOMS,
        )

        # Call LLM
        try:
            raw_response = llm.extract(prompt)
            candidates = llm.parse_json_response(raw_response)
            if not isinstance(candidates, list):
                candidates = []
        except json.JSONDecodeError as e:
            if verbose:
                print(f"       [parse error] {e}")
            errors.append(f"JSON parse: {e}")
            candidates = []
        except Exception as e:
            if verbose:
                print(f"       [LLM error] {e}")
            errors.append(f"LLM: {e}")
            candidates = []

        if verbose:
            print(f"       LLM proposed {len(candidates)} atom(s)")

        atoms_proposed += len(candidates)

        # Write valid candidates
        for candidate in candidates:
            claim = str(candidate.get("claim", "")).strip()
            if not claim or len(claim) > 280 or len(claim) < 15:
                continue

            claim_type = candidate.get("claim_type", "observation")
            if claim_type not in [
                "trend", "tactic", "structural_shift", "failure_mode",
                "metric", "principle", "speculation", "observation"
            ]:
                claim_type = "observation"

            spec = int(candidate.get("speculation_level", 3))
            spec = max(1, min(5, spec))

            conf = float(candidate.get("confidence_score", 0.5))
            conf = max(0.0, min(1.0, conf))

            cross_tags = candidate.get("cross_domain_tags", [])
            if not isinstance(cross_tags, list):
                cross_tags = []

            utility_vector = candidate.get("utility_vector", [])
            if not isinstance(utility_vector, list):
                utility_vector = []

            # Reject atoms with no utility vector — SOUL.md principle
            if not utility_vector:
                if verbose:
                    print(f"       [no utility] Skipped — no utility vector identified")
                continue

            atom_id, is_new_atom = db.insert_atom(
                claim=claim,
                claim_type=claim_type,
                domain=wiz['domain'],
                source_ids=[raw_id],
                epoch_id=epoch['id'],
                model_id=llm.model_info()['extraction_model'],
                extracted_by=f"scout_{wizard_short_name}",
                speculation_level=spec,
                confidence_score=conf,
                cross_domain_tags=cross_tags,
                utility_vector=utility_vector,
                extraction_parameters={
                    "prompt_version": "scout_extraction_v1.0",
                    "provider": llm.model_info()['provider'],
                    "model": llm.model_info()['extraction_model'],
                    "reasoning": candidate.get("reasoning", ""),
                },
            )

            if is_new_atom:
                atoms_written += 1
                if verbose:
                    print(f"       + [{claim_type}] {claim[:65]}...")
            else:
                atoms_duplicate += 1

    # Compute vitality metrics
    acceptance_rate = None
    duplicate_rate = None
    if atoms_proposed > 0:
        acceptance_rate = atoms_written / atoms_proposed
    total_attempted = raw_ingested + atoms_proposed
    if total_attempted > 0:
        duplicate_rate = (raw_duplicate + atoms_duplicate) / (raw_attempted := sources_scanned + atoms_proposed)

    # Anomaly detection
    anomaly_flags = []
    anomaly_severity = "none"

    if atoms_proposed == 0 and sources_scanned > 0:
        anomaly_flags.append({
            "threshold": "zero_output",
            "severity": "warning",
            "detail": f"Scanned {sources_scanned} sources, proposed 0 atoms"
        })
        anomaly_severity = "warning"

    if acceptance_rate is not None and acceptance_rate < 0.20 and atoms_proposed >= 10:
        anomaly_flags.append({
            "threshold": "low_acceptance_rate",
            "severity": "warning",
            "detail": f"Acceptance rate {acceptance_rate:.2%} below 20% threshold"
        })
        anomaly_severity = "warning"

    completed_at = db.now()

    # Write vitality record
    conn = db.governance_db()
    try:
        conn.execute("""
            INSERT INTO cycle_vitality (
                id, wizard_id, wizard_domain, epoch_id,
                started_at, completed_at, duration_seconds,
                cycle_status, sources_scanned, raw_items_ingested,
                raw_items_duplicate, atoms_proposed, atoms_accepted,
                atoms_rejected, atoms_duplicate,
                acceptance_rate, anomaly_flags, anomaly_severity,
                model_id, total_tokens, estimated_cost_usd
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            cycle_id, wiz['id'], wiz['domain'], epoch['id'],
            started_at, completed_at,
            0,  # duration — simplified for Phase 1
            "completed",
            sources_scanned, raw_ingested, raw_duplicate,
            atoms_proposed, atoms_written, 0, atoms_duplicate,
            acceptance_rate,
            json.dumps(anomaly_flags), anomaly_severity,
            llm.model_info()['extraction_model'], 0, 0.0
        ))
        conn.commit()
    finally:
        conn.close()

    # Mark raw items as processed
    vdb = db.vault_db()
    try:
        vdb.execute(
            "UPDATE raw_items SET processing_status='processed' WHERE ingestion_agent=? AND processing_status='pending'",
            (f"scout_{wizard_short_name}",)
        )
        vdb.commit()
    finally:
        vdb.close()

    vitality = {
        "cycle_id": cycle_id,
        "wizard": wiz['name'],
        "domain": wiz['domain'],
        "sources_scanned": sources_scanned,
        "raw_ingested": raw_ingested,
        "raw_duplicate": raw_duplicate,
        "atoms_proposed": atoms_proposed,
        "atoms_written": atoms_written,
        "atoms_duplicate": atoms_duplicate,
        "acceptance_rate": acceptance_rate,
        "anomaly_flags": anomaly_flags,
        "anomaly_severity": anomaly_severity,
    }

    if verbose:
        print(f"\n{'─'*60}")
        print(f"CYCLE COMPLETE — {wiz['name']}")
        print(f"  Sources scanned:  {sources_scanned}")
        print(f"  Raw items new:    {raw_ingested} ({raw_duplicate} duplicates)")
        print(f"  Atoms proposed:   {atoms_proposed}")
        print(f"  Atoms written:    {atoms_written} (candidate status)")
        print(f"  Anomaly:          {anomaly_severity.upper()}")
        if anomaly_flags:
            for f in anomaly_flags:
                print(f"  ⚠ {f['detail']}")
        print(f"\n  Run: python core/scripts/ohara.py review --wizard {wizard_short_name}")
        print(f"{'─'*60}\n")

    return vitality


if __name__ == "__main__":
    import sys
    wizard = sys.argv[1] if len(sys.argv) > 1 else "aria"
    run_cycle(wizard, verbose=True)
