---
name: playwright-reporting-stakeholder
description: Stakeholder-reporting skill for Playwright execution results. Use when Codex needs to turn raw Playwright runs into a concise, non-technical summary of tested scope, release health, business impact, and recommended next actions.
---

# Playwright Stakeholder Reporting

Use this skill when the audience is a product manager, QA lead, or other stakeholder who does not want raw runner noise.

## Inputs

- Playwright HTML, JSON, or CI reports,
- tested scope or release context,
- any known blockers, waived failures, or environment qualifiers.

## Output Contract

Produce a report with:

- `Executive summary`
- `Scope covered`
- `Overall outcome`
- `Known issues and business impact`
- `Recommended next actions`

## Writing Rules

- Translate technical failures into business language.
- Call out confidence limits if the run was partial or environment-constrained.
- Keep stack traces and low-level logs out of the main report unless the user explicitly wants them.
