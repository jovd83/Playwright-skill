---
name: playwright-coverage-matrix-auto-sync
description: Coverage-maintenance skill for Playwright planning and documentation. Use when Codex needs to synchronize coverage plans, scenario IDs, traceability links, and summary counts after tests, requirements, or narrative test documents change.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: coverage-maintenance, playwright-coverage-sync
  dispatcher-accepted-intents: sync_playwright_coverage_artifacts
  dispatcher-input-artifacts: coverage_plan, test_suite, traceability_artifacts
  dispatcher-output-artifacts: updated_coverage_artifacts, sync_report
  dispatcher-stack-tags: playwright, coverage, sync
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# Playwright Coverage Auto-Sync

Use this skill to keep planning artifacts aligned with reality after the suite changes.

## Inputs

- the current coverage plan or matrix,
- the narrative test docs if they exist,
- the implementation references such as `.spec` files, tags, or scenario titles,
- any scenario or requirement IDs already in use.

## Sync Workflow

1. Identify added, removed, renamed, or moved scenarios.
2. Reconcile scenario IDs, anchors, and traceability references across plan, docs, and code.
3. Recalculate summary counts only after the underlying rows are correct.
4. Flag drift explicitly when the plan claims coverage that the implementation cannot prove.

## Output Contract

Report:

- `Updated links and IDs`
- `Count changes`
- `Unmapped requirements or scenarios`
- `Evidence gaps still needing manual resolution`

Use a compact table when helpful:

| Item | Previous | Current | Status | Notes |
|---|---|---|---|---|

## Guardrails

- Do not invent implementation links that you cannot verify.
- Prefer stable scenario IDs over human-readable titles for traceability joins.
- If the repository has no formal matrix yet, state that and propose the smallest useful structure instead of pretending to synchronize one.
