---
name: playwright-reporting-stakeholder
description: Stakeholder-reporting skill for Playwright execution results. Use when Codex needs to turn raw Playwright runs into a concise, non-technical summary of tested scope, release health, business impact, and recommended next actions.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: stakeholder-reporting, playwright-stakeholder-reporting
  dispatcher-accepted-intents: summarize_playwright_test_results
  dispatcher-input-artifacts: execution_results, tested_scope, release_context
  dispatcher-output-artifacts: stakeholder_summary, release_health_report
  dispatcher-stack-tags: playwright, reporting, stakeholder
  dispatcher-risk: low
  dispatcher-writes-files: false
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
