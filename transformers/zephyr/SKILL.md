---
name: playwright-transformer-zephyr
description: Legacy Playwright-specific alias for Zephyr case export. Prefer the standalone `test-artifact-export-skill` skill for transforming approved test cases into Zephyr-ready artifacts, and use this only when Playwright-local conventions must be preserved explicitly.
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

## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `./log-dispatch.cmd --skill <skill_name> --intent <intent> --reason <reason>` (or `./log-dispatch.sh` on Linux)

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