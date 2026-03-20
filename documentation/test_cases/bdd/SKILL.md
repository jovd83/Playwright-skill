---
name: playwright-documentation-bdd
description: Legacy Playwright-specific alias for BDD case formatting. Prefer the standalone `test-artifact-export-skill` skill for Gherkin, BDD, and export-ready case rendering, and use this only when Playwright-local conventions must be preserved explicitly.
---

# Playwright BDD Documentation

Use this skill when the user wants executable-style behavioral documentation in Gherkin form.

## Output Contract

Produce a `.feature`-style artifact with:

- `Feature`
- optional `Background`
- `Scenario` or `Scenario Outline`
- `Examples` when data-driven coverage adds value
- requirement or suite tags when traceability matters

## Writing Rules

- Write behaviors, not UI implementation trivia.
- Keep steps declarative and reusable where possible.
- Use `Scenario Outline` only when the variation is genuinely the same behavior with different data.
- Add negative or resilience scenarios when the requirement carries real risk beyond the happy path.

## Scope

- Stop at documentation unless the user also asked for step definitions or Playwright implementation.
- If the source requirements are incomplete, record assumptions in comments or a short note outside the Gherkin body.
