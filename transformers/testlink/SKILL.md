---
name: playwright-transformer-testlink
description: Legacy Playwright-specific alias for TestLink case export. Prefer the standalone `test-artifact-export-skill` skill for transforming approved test cases into TestLink-ready artifacts, and use this only when Playwright-local conventions must be preserved explicitly.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: test-artifact-formatting, playwright-legacy-export-transform
  dispatcher-accepted-intents: render_test_artifact, export_test_cases
  dispatcher-input-artifacts: approved_test_cases, normalized_test_case_model, destination_constraints
  dispatcher-output-artifacts: transformed_test_artifact, export_bundle
  dispatcher-stack-tags: playwright, transform, legacy-alias
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# TestLink Transformer

Use this skill to convert narrative test cases into TestLink import artifacts.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

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
