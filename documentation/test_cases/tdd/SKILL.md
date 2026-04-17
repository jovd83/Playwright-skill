---
name: playwright-documentation-tdd
description: Legacy Playwright-specific alias for TDD-style case documentation. Prefer the standalone `test-artifact-export-skill` skill for formatting approved test cases or building export-ready artifacts, and use this only when Playwright-local conventions must be preserved explicitly.
metadata:
  author: jovd83
  version: 2.0.0
  dispatcher-category: testing
  dispatcher-capabilities: test-artifact-formatting, playwright-legacy-test-case-formatting
  dispatcher-accepted-intents: render_test_artifact, export_test_cases
  dispatcher-input-artifacts: approved_test_cases, normalized_test_case_model, scenario_list
  dispatcher-output-artifacts: formatted_test_artifact, export_ready_case_set
  dispatcher-stack-tags: playwright, documentation, legacy-alias
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# Playwright TDD Documentation

Use this skill when the user wants structured test-case specs rather than lightweight notes.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

## Output Contract

Produce one scenario document per test case with these fields:

- `title`
- `description`
- `test_suite`
- `covered_requirement`
- `preconditions`
- `steps`
- `execution_type`
- `design_status`
- `test_engineer`
- `test_level`
- `jira`
- `test_script`

Use a markdown step table with `Step`, `Action`, and `Expected result`.

## Traceability Rules

- Use repo-relative automation references such as `tests/e2e/auth/login.spec.ts#AUTH-US02-user-login`.
- Keep requirement references explicit and stable.
- If automation does not exist yet, say so instead of inventing a script link.

## Organization Rules

- Prefer feature- or story-based folders when the user wants a persistent test-doc tree.
- Keep one scenario per file when the docs are meant to be maintained over time.
- Name files after the behavior they describe, not after arbitrary numbering alone.

## Writing Rules

- Preconditions should describe the meaningful starting state, not boilerplate every test shares implicitly.
- Steps should reflect meaningful user or system actions, not every low-level click.
- Expected results should assert the requirement, not generic success language.
