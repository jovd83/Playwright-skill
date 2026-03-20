---
name: playwright-transformer-testrail
description: Legacy Playwright-specific alias for TestRail case export. Prefer the standalone `test-artifact-export-skill` skill for transforming approved test cases into TestRail-ready artifacts, and use this only when Playwright-local conventions must be preserved explicitly.
---

# TestRail Transformer

Use this skill to convert narrative test cases into TestRail import artifacts.

## Inputs

- source scenarios in TDD, BDD, or plain-text form,
- the target TestRail project or section structure when known,
- the chosen import format.

## Output Contract

Produce:

- a TestRail-compatible import artifact, or
- a field-mapping table that shows how each source field will land in TestRail.

## Mapping Rules

- preserve case title, section placement, preconditions, steps, and expected results,
- keep requirement references if the team tracks them in custom fields or notes,
- state any manual follow-up needed for fields that cannot be inferred safely.
