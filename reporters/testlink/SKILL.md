---
name: playwright-reporter-testlink
description: Test-management reporting skill for TestLink. Use when Codex needs to publish Playwright execution results into TestLink using the project's mappings, environment configuration, and chosen reporting flow.
metadata:
  author: jovd83
  version: 2.0.0
  dispatcher-category: testing
  dispatcher-capabilities: test-management-reporting, playwright-test-management-reporting
  dispatcher-accepted-intents: report_playwright_test_results
  dispatcher-input-artifacts: execution_results, test_management_config, mappings
  dispatcher-output-artifacts: published_results, reporting_summary
  dispatcher-stack-tags: playwright, reporting, test-management
  dispatcher-risk: medium
  dispatcher-writes-files: true
---

## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `./log-dispatch.cmd --skill <skill_name> --intent <intent> --reason <reason>` (or `./log-dispatch.sh` on Linux)

# TestLink Reporter

Use this skill when the goal is to push execution outcomes into TestLink.

## Inputs

- TestLink connection details and credentials,
- the local result source,
- the mapping from automated tests to TestLink case IDs,
- any target run, build, or environment context required by the project.

## Workflow

1. Confirm the mapping and target run context.
2. Configure the reporting path or client the project uses.
3. Publish results securely.
4. Return a concise report of what was sent and what could not be reported.

## Guardrails

- Never echo secrets back in plain text.
- Do not report results for tests that cannot be mapped confidently.
- Call out partial publication explicitly.