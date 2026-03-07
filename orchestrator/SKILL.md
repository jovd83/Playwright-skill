---
name: playwright-orchestrator
description: An orchestrator skill that acts as the primary contact point for Playwright testing. It prompts the user for their goals (new tests, existing tests, planning, documenting, etc.) and routes them to the appropriate skills.
---

# Playwright Orchestrator

This skill acts as an intelligent router and test management overseer. Whenever you are asked to handle generic testing tasks, you should start by clarifying the user's intent. 

## Initial Interaction Flow

When starting a testing-related task, unless the user provides enough context upfront, you must ask the user to clarify their specific purpose by presenting these categories. Provide the options clearly to the user:

1. **What is the primary purpose of your testing task today?**
   - **Creating new tests**:
     - For a specific feature/requirements?
     - For everything?
     - Just for sanity testing?
     - Or full regression testing?
     - Or some happy paths?
   - **Agent-defined vs User-defined tests**: 
     - Should I (the AI) define the new scenarios based on requirements?
     - Or are the test cases/scenarios already defined somewhere for me to implement?
   - **Running existing tests**:
     - Run everything?
     - Run a specific part/suite?
   - **Planning tests**: Generate functional coverage plans based on requirements.
   - **Documenting tests**: Document tests using TDD, BDD, or plain text structures.
   - **Transformations & Test Management**: Convert natural language test cases to formats compatible with TestLink, Zephyr, Xray, or TestRail.

2. **Wait for the user's response before proceeding**. Let them clarify their goal based on the menu above.

## Execution and Routing

Once the goal is clarified, leverage the specialized sub-skills in this repository to complete the work:

- **Planning & Requirements Analysis**: Use the `analysis` and `coverage_plan` skills to derive epics/stories and establish functional coverage. Use `coverage_plan/auto-sync` to keep requirements and documentation synchronized.
- **Documentation**: Use `documentation` skills (TDD, BDD, plain text) to write out the formal scenarios. Use `documentation/root_cause` when a test fails.
- **Format Transformation**: Refer to the `transformers` skills to bundle scenarios into CSV/XML/JSON for tools like TestLink, Zephyr, Xray, TestRail.
- **Test Setup & Logic**: Rely on the existing `core`, `pom`, and `ci` skills for best practices in writing resilient Playwright test code. Use `core/preflight.md` for environment readiness and `core/stability-diagnostics.md` for post-failure triage.
- **Reporting Results**: Look for `reporters` (to send automated API reports to test management) or `reporting/stakeholder` (for human-readable summaries).

## 🚨 CRITICAL RULE FOR AI TEST GENERATION 🚨

When you are generating Playwright testing code for the user, you MUST strictly adhere to the **Triad Architecture** (Fixtures + Page Object Models + Stateless Helpers). 
- **POMs FOR REPETITION:** You must encapsulate locators and UI actions inside a Page Object Model (POM) primarily to avoid repetition or for complex UI logic. For simple, one-off test cases with no repetition, inline locators are acceptable.
- All setup/teardown and state management (such as user login via storageState or API) must be handled by **Custom Fixtures**.
- Helper files (`helpers.ts`) must exclusively contain stateless, non-browser functions (e.g. `generateRandomEmail`). Never pass a `Page` object to a helper function.
- **NO PLACEHOLDERS OR STUBS:** You are strictly forbidden from writing "placeholder" tests or using weak assertions like `expect(page).toBeDefined()` or `expect(true).toBe(true)` to claim completion. If the UI or requirements prevent a full implementation, state the blocker clearly instead of providing a fake test. Use legitimate web-first assertions for every generated test scenario.
- **INTEGRATED DIRECTORY STRUCTURE:** All Page Objects, Fixtures, and Helpers MUST be stored within the `tests/` directory (e.g., `tests/page-objects/`) rather than the project root. This ensures the test suite is isolated and portable.

Please deeply review `pom/pom-vs-fixtures-vs-helpers.md` and `core/authentication.md` for the exact implementations of this required architecture.
