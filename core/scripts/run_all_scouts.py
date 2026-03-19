#!/usr/bin/env python3
"""
OHARA — Run All Scout Cycles
Called by systemd timer (ohara-scouts-run.service).
Runs all active wizards in sequence, logs vitality per cycle.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

import db

def main():
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"\n{'═'*50}")
    print(f"OHARA — Scout Run | {started}")
    print(f"{'═'*50}")

    # Import scout here to avoid circular imports at module level
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "scouts"))
    from scout import run_cycle

    wizards = db.list_active_wizards()
    print(f"\nActive wizards: {[w['short_name'] for w in wizards]}")

    results = []
    for w in wizards:
        print(f"\n{'─'*40}")
        print(f"Running: {w['name']} ({w['domain']})")
        print(f"{'─'*40}")
        try:
            vitality = run_cycle(w['short_name'], verbose=True)
            results.append({"wizard": w['short_name'], "status": "ok", "vitality": vitality})
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"wizard": w['short_name'], "status": "error", "error": str(e)})

    # Summary
    print(f"\n{'═'*50}")
    print(f"RUN COMPLETE")
    total_atoms = sum(
        r.get("vitality", {}).get("atoms_written", 0)
        for r in results if r["status"] == "ok"
    )
    errors = [r for r in results if r["status"] == "error"]
    print(f"  Wizards run:   {len(results)}")
    print(f"  Atoms written: {total_atoms}")
    print(f"  Errors:        {len(errors)}")
    if errors:
        for e in errors:
            print(f"  ✗ {e['wizard']}: {e['error'][:60]}")
    print(f"{'═'*50}\n")

if __name__ == "__main__":
    main()
