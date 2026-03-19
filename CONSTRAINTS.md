---
system: Atlas Vault OS
version: 3.1
date: February 19, 2026
status: GOVERNANCE / CONSTRAINTS
dependencies: [[PATTERNS.md]], [[AGENT.md]], [[AUDIT.md]]
---
# CONSTRAINTS.md - Core Operating Constraints

# 1. Strategic Constitution

Ownership Liability
Software is a liability.
Every line of code is maintenance tax.
Build only what is genuinely hard to own.
Prioritize solving acute, recurring pain.

85% Hardening Rule
No task is Done until 85% hardened.
Hardening = passing integration tests + documented edge cases in MEMORY.md + robust error handling.
Unfinished logic ("digital scaffolding") is operational failure.

Spec-Driven Development
Implementation forbidden until TDD.md is approved and locked.
Every spec must be red-teamed (shredded) via AUDIT.md before code is written.

# 2. Economic & Context Constraints

Model Arbitrage
Reasoning tier (high-cost) â†’ architecture, planning, root-cause
Execution tier (balanced) â†’ core logic
Utility tier (low-cost) â†’ tests, docs, re-indexing

Context Traversal
Selective graph load only.
Use YAML frontmatter + headers to determine relevance before full file ingestion.

# 3. Quality & Evidence Constraints

Harness Risk Tiers
High-risk paths â†’ manual sign-off + 100% test coverage
Low-risk paths â†’ automated remediation permitted

Evidence over Claims
UI/frontend changes require machine-verifiable proof (logs, manifests, Playwright traces).
Human claims without evidence are rejected.

# 4. Revenue & Compounding Constraints

Attribution Discipline
Traffic and views are secondary.
Cross-reference distribution with revenue/subscription data.
Scale only patterns that demonstrably drive trials or MRR.
Eliminate vanity drivers.

Failure Compounding
Every production regression â†’ permanent Negative Constraint in SKILLS_COMPOUNDING.md.
System must never repeat the same technical or strategic mistake.

# 5. Final Operating Principle

Systems over Tasks
Do not build tools that execute tasks.
Build systems that manage themselves.
Primary success metrics:
- Silence of the System (autonomous operation time)
- Growth of MRR