---
name: playwright-transformer-testlink
description: Legacy Playwright-specific alias for TestLink case export. Prefer the standalone `test-artifact-export-skill` skill for transforming approved test cases into TestLink-ready artifacts, and use this only when Playwright-local conventions must be preserved explicitly.
---

# TestLink Transformer

Use this skill to convert narrative test cases into TestLink import artifacts.

## Inputs

- source scenarios in TDD, BDD, or plain-text form,
- the target TestLink structure if the project already uses one,
- any required suite, section, or metadata conventions.

## Output Contract

Produce one of:

- a TestLink-compatible XML payload,
- a CSV-style mapping if that is the selected import path,
- a field-mapping table when the user wants the transformation planned before generation.

## Mapping Rules

- map scenario title and summary consistently,
- preserve preconditions, ordered steps, and expected results,
- keep requirement identifiers where TestLink fields allow them,
- call out any source fields that have no clean TestLink destination.
