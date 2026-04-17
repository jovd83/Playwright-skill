---
name: playwright-transformer-xray
description: Legacy Playwright-specific alias for Xray case export. Prefer the standalone `test-artifact-export-skill` skill for transforming approved test cases into Xray-ready artifacts, and use this only when Playwright-local conventions must be preserved explicitly.
metadata:
  author: jovd83
  version: 2.0.0
  dispatcher-category: testing
  dispatcher-capabilities: test-artifact-formatting, playwright-legacy-export-transform
  dispatcher-accepted-intents: render_test_artifact, export_test_cases
  dispatcher-input-artifacts: approved_test_cases, normalized_test_case_model, destination_constraints
  dispatcher-output-artifacts: transformed_test_artifact, export_bundle
  dispatcher-stack-tags: playwright, transform, legacy-alias
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# Xray Transformer

Use this skill to convert narrative test cases into Xray import artifacts.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

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
