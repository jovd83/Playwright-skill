---
name: playwright-coverage-plan-review
description: Coverage-plan review skill for Playwright work. Use when Codex needs to present a proposed coverage plan, surface assumptions and tradeoffs, collect user feedback, and secure explicit approval before large implementation or documentation work.
---

# Playwright Coverage Plan Review

Use this skill to turn a proposed plan into an approved plan.

## Review Workflow

1. Present the plan in a compact, scannable format.
2. Highlight any assumptions, exclusions, or high-cost scenarios.
3. Ask for additions, removals, or reprioritization only where that decision matters.
4. Record the approved scope clearly before downstream work begins.

## Output Contract

Summarize the plan with:

- `Included coverage`
- `Assumptions`
- `Proposed exclusions or deferred items`
- `Questions requiring a decision`

When helpful, include an updated approval table:

| Requirement ID | Scenario | Priority | Status | Notes |
|---|---|---|---|---|

Use `Status` values such as `proposed`, `approved`, `deferred`, or `removed`.

## Approval Rules

- If the user already approved the scope in the same thread, do not force a second approval loop.
- If the plan is large, costly, or assumption-heavy, get explicit approval before implementation.
- If feedback changes the plan materially, refresh the presented version before proceeding.
