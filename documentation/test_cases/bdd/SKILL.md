---
name: playwright-documentation-bdd
description: A skill to document Playwright test cases using the BDD (Behavior-Driven Development) Gherkin syntax.
---

# Documenting Test Cases: BDD (Gherkin) format

This skill ensures that test scenarios are documented using the standardized Given-When-Then BDD syntax.

## Structure

When asked to document a test case in BDD format, you must generate a markdown or `.feature` file following the standard Gherkin keywords:

### Feature
A high-level description of a software feature.
*Example: Feature: User Authentication*

### Scenario / Scenario Outline
A concrete example illustrating how the software should behave.
*Example: Scenario: Failed login with invalid credentials*

### Given
The initial context or state of the system.
*Example: Given the user is on the login page*

### When
An event or an action taken by the user.
*Example: When the user enters "invalid@test.com" and "wrongpass"*
*And clicks the login button*

### Then
An expected outcome.
*Example: Then an error message "Invalid credentials" is displayed*

### And / But
Keywords used to extend Given, When, or Then steps without repeating them.

### Background
Steps that are common to all scenarios within the feature file, executed before each scenario.

### Scenario Outline & Examples
Used for data-driven testing, executing the same scenario multiple times with different sets of data. Placeholders `<param>` are filled from an `Examples:` table.
*Example:*
```gherkin
Scenario Outline: Login attempts
  When the user enters "<username>" and "<password>"
  Then the result is "<status>"

  Examples:
    | username | password | status  |
    | admin    | pwd123   | success |
    | user     | badpwd   | failure |
```

### Tags
Used to categorize scenarios (e.g., `@smoke`, `@regression`, `@US-101`) enabling selective execution.

### Data Tables
Allows passing structured arrays directly within a single step (represented with `|`).

## Best Practices
- Keep statements simple and declarative.
- Avoid UI-specific jargon (e.g., "Given I click the blue div with id user-form") and focus on behavior (e.g., "Given the user submits the form").
- Add specific requirement tags (e.g., `@US-101`) above the Scenario.

**CRITICAL**: You must generate multiple scenarios for each requirement to ensure robustness. A 1-to-1 mapping (one story to one test) is usually insufficient. For every User Story/Requirement, generate **at least 3 scenarios** (unless trivial):
1. **MSS (Main Success Scenario)**: The happy path using standard data.
2. **EXT (Extension/Variation)**: Valid variations (e.g., required + optional fields).
3. **ERR (Error/Negative)**: Invalid inputs, validation errors, or unauthorized states.

Use **Scenario Outline** and **Examples** where appropriate to cover multiple data variations efficiently.

## Usage
Produce this documentation inside a `docs/features/` or `tests/features/` folder as instructed by the user. Do not write the Playwright step definitions until this scenario is approved.
