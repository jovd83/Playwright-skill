---
name: playwright-transformer-xray
description: Legacy Playwright-specific alias for Xray case export. Prefer the standalone `test-artifact-export-skill` skill for transforming approved test cases into Xray-ready artifacts, and use this only when Playwright-local conventions must be preserved explicitly.
---

# Xray Transformer

Use this skill to convert narrative test cases into Xray import artifacts.

## Inputs

- source scenarios in TDD, BDD, or plain-text form,
- whether the target should be `Manual` or `Cucumber` style,
- project or requirement linkage details if they are already known.

## Output Contract

Produce:

- an Xray-compatible payload,
- or a field-mapping table showing how the source maps into Xray test fields and links.

## Mapping Rules

- use Xray test type intentionally,
- preserve ordered steps and expected results for manual tests,
- preserve tags and requirement links when they are available,
- avoid inventing Jira linkage the user has not provided.
