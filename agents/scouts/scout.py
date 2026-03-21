#!/usr/bin/env python3
"""
OHARA — Scout Agent
Nutzt Source Adapters (HackerNews, RSS, Reddit, X).
Prinzip: API or Feed first. Browser second. Scraping last.
"""

import json
import time
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core" / "scripts"))

import db
import llm
from adapters import get_adapters_for_wizard

MAX_SOURCES   = int(os.getenv("SCOUT_MAX_SOURCES_PER_CYCLE", "10"))
MAX_ATOMS     = int(os.getenv("SCOUT_MAX_ATOMS_PER_SOURCE", "5"))

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

SOURCE: {url}
---
{content}
---

Extract 0 to {max_atoms} atoms. If nothing is genuinely worth preserving, return [].

For each atom return:
- claim: string, max 280 chars
- claim_type: trend|tactic|structural_shift|failure_mode|metric|principle|speculation|observation
- speculation_level: 1-5 (1=strong evidence, 5=pure speculation)
- confidence_score: 0.0-1.0
- cross_domain_tags: array of other domains this resonates in
- utility_vector: array from [product_building, process_improvement, system_enhancement, financial, future_optionality, personal_capability, creative_enabling, decision_support, self_improvement]
- reasoning: one sentence why this is worth preserving

Respond ONLY with a JSON array. If nothing: []"""


def run_cycle(wizard_short_name: str, verbose: bool = True) -> dict:
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

    sources_scanned = 0
    raw_ingested = 0
    raw_duplicate = 0
    atoms_proposed = 0
    atoms_written = 0
    atoms_duplicate = 0

    # Get adapters for this wizard
    adapters = get_adapters_for_wizard(wiz)
    if verbose:
        print(f"Adapters: {[type(a).__name__ for a in adapters]}")

    # Fetch from all adapters
    all_items = []
    for adapter in adapters:
        try:
            items = adapter.fetch(limit=MAX_SOURCES // len(adapters) + 2)
            all_items.extend(items)
            if verbose:
                print(f"  {type(adapter).__name__}: {len(items)} items")
        except Exception as e:
            if verbose:
                print(f"  {type(adapter).__name__}: failed — {e}")

    if verbose:
        print(f"\nTotal sources fetched: {len(all_items)}")

    # Process each item
    for item in all_items[:MAX_SOURCES]:
        sources_scanned += 1

        if verbose:
            print(f"\n  [{sources_scanned}] {item.url[:70]}")

        # Ingest to vault
        content_bytes = item.text.encode("utf-8")
        raw_id, is_new = db.insert_raw_item(
            origin_url=item.url,
            domain=wiz['domain'],
            content=content_bytes,
            content_type="text",
            source_tier=item.source_tier,
            ingestion_agent=f"scout_{wizard_short_name}",
            epoch_id=epoch['id'],
            editorial_independence=item.independence_score,
        )

        if not is_new:
            raw_duplicate += 1
            if verbose:
                print(f"       [dup] Already in vault")
            continue

        raw_ingested += 1

        if len(item.text) < 80:
            if verbose:
                print(f"       [skip] Too short")
            continue

        # LLM extraction
        prompt = EXTRACTION_PROMPT.format(
            wizard_name=wiz['name'],
            persona_summary=wiz['persona_summary'],
            domain=wiz['domain'],
            url=item.url,
            content=item.text[:6000],
            max_atoms=MAX_ATOMS,
        )

        try:
            raw_response = llm.extract(prompt)
            candidates = llm.parse_json_response(raw_response)
            if not isinstance(candidates, list):
                candidates = []
        except Exception as e:
            if verbose:
                print(f"       [LLM error] {e}")
            candidates = []

        if verbose:
            print(f"       LLM proposed {len(candidates)} atom(s)")

        atoms_proposed += len(candidates)

        for candidate in candidates:
            claim = str(candidate.get("claim", "")).strip()
            if not claim or len(claim) > 280 or len(claim) < 15:
                continue

            claim_type = candidate.get("claim_type", "observation")
            if claim_type not in ["trend","tactic","structural_shift","failure_mode",
                                   "metric","principle","speculation","observation"]:
                claim_type = "observation"

            spec = max(1, min(5, int(candidate.get("speculation_level", 3))))
            conf = max(0.0, min(1.0, float(candidate.get("confidence_score", 0.5))))
            cross_tags = candidate.get("cross_domain_tags", [])
            utility_vector = candidate.get("utility_vector", [])

            if not utility_vector:
                if verbose:
                    print(f"       [no utility] Skipped")
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
                cross_domain_tags=cross_tags if isinstance(cross_tags, list) else [],
                utility_vector=utility_vector,
                extraction_parameters={
                    "prompt_version": "scout_extraction_v1.0",
                    "provider": llm.model_info()['provider'],
                    "model": llm.model_info()['extraction_model'],
                    "source": item.source_name,
                    "reasoning": candidate.get("reasoning", ""),
                },
            )

            if is_new_atom:
                atoms_written += 1
                if verbose:
                    print(f"       + [{claim_type}] {claim[:65]}...")
            else:
                atoms_duplicate += 1

    # Anomaly detection
    anomaly_flags = []
    anomaly_severity = "none"
    acceptance_rate = atoms_written / atoms_proposed if atoms_proposed > 0 else None

    if atoms_proposed == 0 and sources_scanned > 0:
        anomaly_flags.append({"threshold": "zero_output", "severity": "warning",
                              "detail": f"Scanned {sources_scanned} sources, 0 atoms proposed"})
        anomaly_severity = "warning"

    if acceptance_rate is not None and acceptance_rate < 0.20 and atoms_proposed >= 10:
        anomaly_flags.append({"threshold": "low_acceptance_rate", "severity": "warning",
                              "detail": f"Rate {acceptance_rate:.1%} below 20%"})
        anomaly_severity = "warning"

    # Write vitality record
    conn = db.governance_db()
    try:
        conn.execute("""
            INSERT INTO cycle_vitality (
                id, wizard_id, wizard_domain, epoch_id,
                started_at, completed_at, duration_seconds, cycle_status,
                sources_scanned, raw_items_ingested, raw_items_duplicate,
                atoms_proposed, atoms_accepted, atoms_rejected, atoms_duplicate,
                acceptance_rate, anomaly_flags, anomaly_severity,
                model_id, total_tokens, estimated_cost_usd
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            cycle_id, wiz['id'], wiz['domain'], epoch['id'],
            started_at, db.now(), 0, "completed",
            sources_scanned, raw_ingested, raw_duplicate,
            atoms_proposed, atoms_written, 0, atoms_duplicate,
            acceptance_rate, json.dumps(anomaly_flags), anomaly_severity,
            llm.model_info()['extraction_model'], 0, 0.0
        ))
        conn.commit()
    finally:
        conn.close()

    # Mark raw items processed
    vdb = db.vault_db()
    try:
        vdb.execute(
            "UPDATE raw_items SET processing_status='processed' WHERE ingestion_agent=? AND processing_status='pending'",
            (f"scout_{wizard_short_name}",)
        )
        vdb.commit()
    finally:
        vdb.close()

    if verbose:
        print(f"\n{'─'*60}")
        print(f"CYCLE COMPLETE — {wiz['name']}")
        print(f"  Sources scanned:  {sources_scanned}")
        print(f"  Raw items new:    {raw_ingested} ({raw_duplicate} dup)")
        print(f"  Atoms proposed:   {atoms_proposed}")
        print(f"  Atoms written:    {atoms_written}")
        print(f"  Anomaly:          {anomaly_severity.upper()}")
        if anomaly_flags:
            for f in anomaly_flags:
                print(f"  ⚠ {f['detail']}")
        print(f"{'─'*60}\n")

    return {
        "cycle_id": cycle_id,
        "wizard": wiz['name'],
        "domain": wiz['domain'],
        "sources_scanned": sources_scanned,
        "atoms_written": atoms_written,
        "anomaly_severity": anomaly_severity,
    }


if __name__ == "__main__":
    wizard = sys.argv[1] if len(sys.argv) > 1 else "aria"
    run_cycle(wizard, verbose=True)
