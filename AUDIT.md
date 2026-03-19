---
system: Atlas Vault OS
version: 3.1
date: February 19, 2026
status: COMMAND_REF / PLAYBOOKS
dependencies: [[AGENT.md]], [[PATTERNS.md]], [[CONSTRAINTS.md]]
---
# PLAYBOOKS.md - Command & Workflow Reference

# 1. Command Center
Tiered commands; cap at $0.50/task.

| Command | Purpose | Model Tier | Node |
|---------|---------|------------|------|
| /REINDEX | Refresh graph | Utility | Global |
| /SPECIFY | Lock architecture | Reasoning | TDD.md |
| /SHRED | Red-team plan | Reasoning | AUDIT.md |
| /PLAN | Micro-steps | Balanced | IMPLEMENTATION_PLAN.md |
| /EXECUTE | Implement | Balanced | SESSION_LOGS.md |
| /AUDIT | Hardening gate | Reasoning | AUDIT.md |
| /MARKET | Attribution | Balanced | PATTERNS.md |
| /SKILL | Compound failure | Balanced | SKILLS_COMPOUNDING.md |
| /REMEDIATE | Restore | Reasoning | RECOVERY_KIT.md |

# 2. Operational Playbooks

Initialization Phase
- /REINDEX: Scan YAML/headers.
- Interrogate: Flag assumptions.
- /SPECIFY: Freeze in TDD.md.

Shred Phase
- /SHRED: Break logic/security.
- Constraint: No execution until resolved.
- Define risk in harness.json.

Action Phase
- Loop: Claim > Plan > Implement > Test.
- Utility tier for tests/docs.
- /MARKET: Cross-ref revenue.

Closing Phase
- /AUDIT: Verify 85%.
- /SKILL: Add constraint.
- Journal: Update MEMORY.md.
- Diagnostics: Flag high uptime/low output.

# 3. File Hierarchy (Skill Graph)
YAML required for scans.

Governance: AGENT.md, PATTERNS.md, CONSTRAINTS.md, AUDIT.md, PLAYBOOKS.md.

Foundations: SKILLS_COMPOUNDING.md, TECHSTACK.md, RECOVERY_KIT.md.

Workflow: CONCEPT.md, IMPLEMENTATION_PLAN.md, TDD.md, MEMORY.md, SESSION_LOGS.md.

# 4. PR Loop
1. Review headSha.
2. /REMEDIATE if findings.
3. Hardening check: Backend access revoked.
4. CI fanout on clean state.

Final Principle: Discipline over inspiration.
Halt on ambiguity. No guesses.

Update Protocol: Add commands via PATTERNS.md supersede.