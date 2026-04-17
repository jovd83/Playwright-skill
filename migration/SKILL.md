---
name: playwright-migration
description: Migration skill for moving existing UI automation to Playwright. Use when Codex needs to translate Cypress or Selenium/WebDriver patterns, plan incremental migration, preserve coverage during framework change, or explain architectural differences that affect the suite design.
metadata:
  author: jovd83
  version: 2.0.0
  dispatcher-category: testing
  dispatcher-capabilities: framework-migration, playwright-migration
  dispatcher-accepted-intents: migrate_to_playwright
  dispatcher-input-artifacts: source_test_suite, repo_context, migration_scope
  dispatcher-output-artifacts: migration_plan, migrated_tests, compatibility_notes
  dispatcher-stack-tags: playwright, migration, framework
  dispatcher-risk: high
  dispatcher-writes-files: true
---

## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `./log-dispatch.cmd --skill <skill_name> --intent <intent> --reason <reason>` (or `./log-dispatch.sh` on Linux)

# Playwright Migration

Use this skill when the user is moving from another browser automation stack to Playwright.

## Migration Workflow

1. Inventory the existing suite structure, runner assumptions, and shared helpers.
2. Map framework concepts to the Playwright equivalents.
3. Choose an incremental migration path that preserves confidence.
4. Revisit architecture decisions such as fixtures, waiting, locators, and CI once the syntax translation is done.

## Guides

| Source framework | Guide |
|---|---|
| Cypress | [from-cypress.md](from-cypress.md) |
| Selenium / WebDriver | [from-selenium.md](from-selenium.md) |

## Output Bias

Prefer migration plans, translated examples, and architecture notes over abstract comparisons.