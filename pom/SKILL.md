---
name: playwright-pom
description: Page Object Model patterns for Playwright — when to use POM, how to structure page objects, and when fixtures or helpers are a better fit.
---

# Playwright Page Object Model

> Structure your test code for maintainability — know when POM helps and when simpler patterns win.

**2 guides** covering Page Object Model implementation and the decision framework for choosing between POM, fixtures, and helpers.

## 🚨 MANDATORY ARCHITECTURE: The Triad 🚨

All tests in this project MUST follow the **Triad Architecture**. This structure is designed to eliminate boilerplate, ensure maintainability, and prevent fragile tests.

1.  **Fixtures (`test.extend`)**: The **only** way to manage state, setup, and teardown. This includes authentication (`asUser`, `asAdmin`), database seeding, and providing Page Objects to the test.
2.  **Page Object Models (POMs)**: Use POMs primarily to avoid repetition across tests or for complex UI logic. For simple, one-off test cases with no repetition, inline locators are acceptable. Repeated UI interactions MUST always be encapsulated in POMs.
3.  **Stateless Helper Functions**: Pure utility functions with **NO browser interaction**. Used for data generation (e.g., `randomEmail`), calculations, or formatting. Never pass a `Page` object to a helper.
4.  **Integrated Directory Layout**: All POMs, Fixtures, and Helpers MUST be stored within the `tests/` directory (e.g., `tests/page-objects/`, `tests/fixtures/`, `tests/helpers/`). Do not place them in the project root.

## Guide Index

| Topic | Guide |
|---|---|
| Page Object Model patterns | [page-object-model.md](page-object-model.md) |
| POM vs fixtures vs helpers | [pom-vs-fixtures-vs-helpers.md](pom-vs-fixtures-vs-helpers.md) |
| Architecture Decision | [core/test-architecture.md](../core/test-architecture.md) |

---

**Summary Strategy**: If you are writing a test, you should only see POM methods and assertions. If you are setting up state, use a fixture. If you are generating data, use a helper. 
