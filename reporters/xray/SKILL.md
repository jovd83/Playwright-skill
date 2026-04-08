---
name: playwright-reporter-xray
description: Test-management reporting skill for Xray. Use when Codex needs to publish Playwright execution results into Xray or Jira using the project's mappings, import format, and chosen reporting flow.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: test-management-reporting, playwright-test-management-reporting
  dispatcher-accepted-intents: report_playwright_test_results
  dispatcher-input-artifacts: execution_results, test_management_config, mappings
  dispatcher-output-artifacts: published_results, reporting_summary
  dispatcher-stack-tags: playwright, reporting, test-management
  dispatcher-risk: medium
  dispatcher-writes-files: true
---

# Xray Reporter

Use this skill when the goal is to push execution outcomes into Xray.

## Inputs

- Xray or Jira connection details and credentials,
- the local result source,
- the mapping from automated tests to Xray keys,
- the chosen import format or reporter path,
- any target execution or project context required by the project.

## Workflow

1. Confirm the mapping and target execution context.
2. Configure the reporting path or export format the project uses.
3. Publish results securely.
4. Return a concise report of what was sent and what could not be reported.

## Guardrails

- Never echo secrets back in plain text.
- Do not report results for tests that cannot be mapped confidently.
- Call out partial publication explicitly.
