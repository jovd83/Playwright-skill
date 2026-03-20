---
name: playwright-analysis-requirements
description: Requirements-analysis skill for Playwright planning and implementation. Use when Codex needs to extract testable behaviors, acceptance criteria, risks, dependencies, or open questions from tickets, specs, markdown docs, or other requirement sources before writing tests or coverage plans.
---

# Playwright Requirements Analysis

Use this skill to turn raw product or engineering artifacts into a trustworthy testing baseline.

## Inputs

Use the best available sources in this order:

1. user-provided tickets, specs, or links,
2. repository-local docs such as `docs/`, markdown files, issue exports, or feature notes,
3. adjacent automation or product artifacts that clarify behavior.

Do not keep searching indefinitely once you have enough evidence to form a reliable baseline.

## Output Contract

Produce a concise requirements baseline with these sections:

1. `Confirmed behaviors`
2. `Inferred behaviors`
3. `Risks and edge cases`
4. `Open questions or missing evidence`
5. `Source evidence`

When tabular output helps, use:

| Requirement ID | Behavior | Evidence | Confidence | Notes |
|---|---|---|---|---|

## Rules

- Separate confirmed facts from reasonable inference.
- Normalize vague prose into testable behaviors.
- Capture edge cases, authorization rules, data constraints, and failure modes when the source implies them.
- Call out missing or contradictory evidence explicitly instead of hiding it inside the summary.

## When to Pause

- Pause for confirmation when the requirements are ambiguous enough to change the downstream plan materially.
- If the user explicitly asked for a baseline only, stop after the analysis.
- If the requirements are clear enough and the user asked for downstream planning in the same request, continue while marking assumptions.

## Handoff

Use the output of this skill as the input to [../coverage_plan/generation/SKILL.md](../coverage_plan/generation/SKILL.md) or to direct implementation work when the scope is already narrow.
