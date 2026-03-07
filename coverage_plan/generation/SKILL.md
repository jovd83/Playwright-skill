---
name: playwright-coverage-plan-generation
description: A skill to generate a functional coverage plan mapping the confirmed requirements to necessary Playwright test scenarios.
---

# Functional Coverage Plan Generation

This skill provides a structured approach to generating a coverage plan from the confirmed requirements.

## 1. Prerequisite
Ensure that you have successfully completed the `playwright-analysis-requirements` skill phase and that the user has verified the Acceptance Criteria (AC).

## 2. Generate the Scenarios
For each accepted Epic, User Story, or AC, generate a list of distinct test scenarios.
You MUST aim for functional completeness. Do not restrict yourself to just one "happy path" per requirement.

**Coverage Guidelines**:
1. **Standard workflows**: The primary and most common usage paths.
2. **Alternative Variations**: Valid deviations, such as including optional fields, using different valid input combinations, or different user roles.
3. **Resilience & Error Handling**: Validation errors, invalid inputs, unauthorized states, and error recovery.
4. **Data Boundaries**: Limits, maximum/minimum inputs, and edge cases.

**Decision Logic for Testing Depth**:
- **High-Value/Logic-Heavy Features**: (e.g., Auth, Payments, CRUD, Multi-step forms) Always provide a suite of scenarios covering both success and failure modes. 
- **Simple UI-Only Features**: (e.g., static "About" page, simple display labels) A single verification is sufficient.
- **AI Principle**: If a requirement has inputs or business logic, it almost always has more than one meaningful execution path. Do not force redundant tests, but never omit meaningful "unhappy" or "alternative" paths just to minimize effort. Aim for high-fidelity coverage that builds confidence.

## 3. Formatting the Plan
Structure the output using markdown tables mapping the `Requirement/AC ID` to the `Proposed Test Scenario` and the `Execution Type` (UI / API / Component).

## 4. Next Step
Proceed to use the `playwright-coverage-plan-review` skill to present this generated plan to the user.
