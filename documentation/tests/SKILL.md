---
name: playwright-documentation-tests
description: Automation-code documentation skill for Playwright suites. Use when Codex needs to add or improve human-readable comments, docblocks, or file-level explanations around existing Playwright tests without drowning the code in redundant commentary.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: automation-documentation, playwright-test-documentation
  dispatcher-accepted-intents: document_playwright_tests
  dispatcher-input-artifacts: test_suite, repo_context, traceability_artifacts
  dispatcher-output-artifacts: automation_docs, documentation_update
  dispatcher-stack-tags: playwright, documentation, automation
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# Playwright Automation Documentation

Use this skill to improve readability of existing Playwright code.

## Workflow

1. Read the target test file or support module first.
2. Identify where comments would materially help a future maintainer.
3. Add concise documentation at the file, suite, test, fixture, or helper level as appropriate.

## Commenting Rules

- Prefer high-signal docblocks over line-by-line narration.
- Explain intent, scope, or non-obvious behavior.
- Do not restate code that is already obvious from the test title or method name.
- Avoid comment spam in straightforward tests.

## Output

After editing, summarize:

- what was documented,
- why those locations mattered,
- any parts of the suite that are still hard to understand and may need refactoring rather than more comments.
