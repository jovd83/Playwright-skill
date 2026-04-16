---
name: playwright-documentation-root-cause
description: Failure-analysis skill for Playwright runs. Use when Codex needs to investigate a failing test, distinguish likely product bugs from test issues, and produce a concise developer-focused root-cause report backed by evidence.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: failure-analysis, playwright-root-cause
  dispatcher-accepted-intents: analyze_playwright_test_failure
  dispatcher-input-artifacts: failure_output, repo_context, test_artifacts
  dispatcher-output-artifacts: root_cause_report, failure_summary
  dispatcher-stack-tags: playwright, diagnostics, failure-analysis
  dispatcher-risk: low
  dispatcher-writes-files: false
---

# Playwright Root Cause Analysis

Use this skill when a failure needs explanation, not just rerunning.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

## Inputs

- failing test output,
- trace artifacts, screenshots, videos, or HTML reports when available,
- related console, network, or application logs,
- recent code or requirement changes if they help explain the failure.

## Analysis Workflow

1. Identify the failing assertion or stopping point.
2. Reconstruct what the app and test were each expecting.
3. Classify the issue as likely `product bug`, `test defect`, `environment issue`, or `possible flake`.
4. Support the classification with concrete evidence.

## Output Contract

Provide:

- `Failure`
- `Most likely cause`
- `Classification`
- `Evidence`
- `Recommended next action`
- `Confidence`

## Guardrails

- Do not claim certainty when the evidence is mixed.
- Separate observation from hypothesis.
- If the right answer is "needs reproduction with more data," say that directly.
