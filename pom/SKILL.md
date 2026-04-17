---
name: playwright-pom
description: Test-architecture skill for Playwright page objects, fixtures, and helpers. Use when Codex needs to decide whether to introduce a Page Object Model, how to structure page objects, and how to separate browser state, UI behavior, and stateless utilities cleanly.
metadata:
  author: jovd83
  version: 2.0.0
  dispatcher-category: testing
  dispatcher-capabilities: test-architecture, playwright-pom-design
  dispatcher-accepted-intents: design_playwright_test_architecture
  dispatcher-input-artifacts: repo_context, suite_structure, reuse_patterns
  dispatcher-output-artifacts: architecture_guidance, pom_design, fixture_strategy
  dispatcher-stack-tags: playwright, architecture, pom
  dispatcher-risk: medium
  dispatcher-writes-files: false
---

## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `./log-dispatch.cmd --skill <skill_name> --intent <intent> --reason <reason>` (or `./log-dispatch.sh` on Linux)

# Playwright POM

Use this skill when the main decision is architectural rather than tactical.

## Decision Model

- Use fixtures for setup, teardown, shared state, and authenticated contexts.
- Use page objects to encapsulate repeated or complex UI behavior.
- Use helpers only for stateless utilities such as data generation, formatting, or pure transformations.
- Do not force page objects for every one-off interaction.

## Practical Rules

1. Reach for a page object when the same UI behavior appears in multiple tests or when the page flow is complex enough to deserve a named abstraction.
2. Keep assertions close to the test unless a reusable page-level assertion adds clarity.
3. Avoid helpers that accept a `Page` or mutate browser state.
4. Keep the testing support code organized with the tests it serves.

## Read by Need

| Need | Guide |
|---|---|
| Page object design | [page-object-model.md](page-object-model.md) |
| POM vs fixture vs helper tradeoffs | [pom-vs-fixtures-vs-helpers.md](pom-vs-fixtures-vs-helpers.md) |
| Broader architecture decisions | [../core/test-architecture.md](../core/test-architecture.md) |