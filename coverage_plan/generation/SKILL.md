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
You must cover (if usefull):
1. **Happy Paths (MSS)**: The primary and most common workflows using standard/required data.
2. **Alternative Paths (EXT)**: Valid deviations, such as including optional fields or different valid input combinations.
3. **Negative/Error Paths (ERR)**: Form validation errors, unauthorized access, invalid inputs, and error handling.
4. **Boundary Values**: Limits, maximum inputs, and edge cases.

**Decision Logic for Testing Depth**:
- **Complex/High-Risk Features**: (e.g., Auth, Payments, CRUD) **MUST** have multiple scenarios (MSS, EXT, ERR).
- **Trivial/Low-Risk Features**: (e.g., static "About" page, simple display labels) A single Happy Path (MSS) is sufficient.
- **AI Discretion**: Evaluate the requirement's complexity. If a story has no optional fields and no logical error paths, do not force redundant tests. Aim for high-fidelity coverage without over-engineering.

## 3. Formatting the Plan
Structure the output using markdown tables mapping the `Requirement/AC ID` to the `Proposed Test Scenario` and the `Execution Type` (UI / API / Component).

## 4. Next Step
Proceed to use the `playwright-coverage-plan-review` skill to present this generated plan to the user.
