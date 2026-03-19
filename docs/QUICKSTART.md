# OHARA — Phase 1 Quickstart
## Operating as a Wizard (Manual Calibration)

---

## Prerequisites

```bash
# Install dependencies
pip install click rich

# Initialize databases (first time only)
python core/db/migrations/migrate.py

# Seed wizards, epoch, prompts (first time only)
python core/db/seed/seed.py

# Run acceptance tests (must be 31/31 green)
python tests/schema/test_schema.py
```

---

## Your Working Directory

```
cd ohara/
python core/scripts/ohara.py <command>
```

All commands run from the `ohara/` root.

---

## Daily Workflow (You as a Wizard)

### 1. Check library status
```bash
python core/scripts/ohara.py status
```

### 2. Find a source, ingest it
```bash
# Example: Aria finds an interesting HackerNews thread
python core/scripts/ohara.py ingest \
  --wizard aria \
  --url https://news.ycombinator.com/item?id=12345 \
  --tier secondary \
  --independence 0.6
```
Returns a `raw_item_id` like `raw_a3f2b1...`

### 3. Extract an atom from the source
```bash
python core/scripts/ohara.py atom create \
  --wizard aria \
  --raw raw_a3f2b1...
```
Interactive prompts walk you through:
- Writing the claim (max 280 chars, be specific)
- Choosing claim type
- Setting speculation level (1-5)
- Setting confidence score (0.0-1.0)
- Flagging cross-domain resonance

### 4. Review pending atoms
```bash
# Review your domain
python core/scripts/ohara.py review --wizard aria

# Or review a specific domain
python core/scripts/ohara.py review --domain ai_patterns
```
For each atom: `a` = accept | `r` = reject (requires reason) | `s` = skip | `q` = quit

### 5. Create a pattern (once you have 3+ accepted atoms on a theme)
```bash
python core/scripts/ohara.py pattern create --wizard aria
```

### 6. List what exists
```bash
# All atoms in a domain
python core/scripts/ohara.py atom list --domain ai_patterns

# Accepted atoms only
python core/scripts/ohara.py atom list --domain ai_patterns --status accepted

# All patterns
python core/scripts/ohara.py pattern list

# Patterns at a specific status
python core/scripts/ohara.py pattern list --status emerging
```

---

## Your God Interface

```bash
# Daily digest — what needs attention
python core/scripts/ohara.py god digest

# Approve a VALIDATED pattern for STRUCTURAL status (your exclusive action)
python core/scripts/ohara.py god approve --pattern pat_xxxx

# Redirect a wizard
python core/scripts/ohara.py god redirect \
  --wizard sterling \
  --instruction "Focus more on ETF structural patterns, less on individual stock picks"
```

---

## Wizard Reference

| Short Name | Full Name     | Domain                   |
|------------|---------------|--------------------------|
| aria       | Aria Chen     | ai_patterns              |
| marcus     | Marcus Reeves | software_architecture    |
| nova       | Nova Patel    | saas_product             |
| sterling   | Sterling Voss | finance_investing        |
| reina      | Reina Solano  | marketing_distribution   |

---

## Phase 1 Calibration Goals (4 weeks)

Track these manually. They become the locked thresholds for Phase 2.

| Metric                          | Target                  |
|---------------------------------|-------------------------|
| Atoms accepted                  | 50+ total, 3+ domains   |
| Your acceptance rate            | Expect 30-60%           |
| Patterns in EMERGING+           | 5+ total                |
| Skeptic cycles completed        | 2+                      |
| Counter-evidence records        | At least 1 per pattern  |

**Rule:** Log your reasoning for every accept/reject decision.
That reasoning becomes the calibration data.

---

## What Makes a Good Atom

Ask yourself before committing:
- Is this claim specific enough that a stranger would understand it without context?
- Would a genuine expert in this domain find this non-obvious?
- Does this hold true across multiple contexts or is it a one-time observation?
- Could this be useful to someone building, investing, or making decisions in 2 years?

If yes to all four → commit it.
If unsure → lower the confidence score and set speculation_level higher.
If no → reject it. Log why.

---

## The Core Question (Never Forget)

> When can something be called knowledge?

Not information. Not signal. Not content.
**Knowledge**: structurally true, domain-tested, useful beyond the moment it was found.

That question is what you're calibrating.
