---
name: playwright-transformer-zephyr
description: Legacy Playwright-specific alias for Zephyr case export. Prefer the standalone `test-artifact-export-skill` skill for transforming approved test cases into Zephyr-ready artifacts, and use this only when Playwright-local conventions must be preserved explicitly.
---

# Zephyr Transformer

Use this skill to convert narrative test cases into Zephyr Scale import artifacts.

## Inputs

- source scenarios in TDD, BDD, or plain-text form,
- the chosen Zephyr import path,
- any project-specific field expectations.

## Output Contract

Produce:

- a Zephyr-compatible import artifact, or
- a field-mapping table that shows the exact transformation.

## Mapping Rules

- map scenario name, objective, preconditions, step script, and expected results consistently,
- preserve requirement references when the destination format supports them,
- call out any information the source material does not provide.
