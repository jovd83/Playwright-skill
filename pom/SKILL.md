---
name: playwright-pom
description: Test-architecture skill for Playwright page objects, fixtures, and helpers. Use when Codex needs to decide whether to introduce a Page Object Model, how to structure page objects, and how to separate browser state, UI behavior, and stateless utilities cleanly.
---

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
