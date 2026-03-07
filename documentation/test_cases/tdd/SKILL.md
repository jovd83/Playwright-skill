---
name: playwright-documentation-tdd
description: A skill to document Playwright test cases in a standard TDD (Test-Driven Development) format.
---

# Documenting Test Cases: TDD format

This skill ensures that test cases are uniformly documented using a standardized structure that supports high-fidelity traceability and organization.

## 1. Storage & Organization

To maintain a scalable documentation suite, tests **must** be stored in a hierarchical structure based on features or epics:

- **Root Directory**: `docs/tests/`
- **Sub-folders**: One folder per Epic or Feature (matching the `tests/` automation structure).
- **Files**: One `.md` file per **test scenario**. Files should be grouped in sub-folders named after the User Story or Feature they cover.
**Decision Logic for Testing Depth**:
- **Complex/High-Risk Features**: (e.g., Auth, Payments, CRUD) **MUST** have multiple scenarios (MSS, EXT, ERR).
- **Trivial/Low-Risk Features**: (e.g., static "About" page, simple display labels) A single Happy Path (MSS) is sufficient.
- **AI Discretion**: Evaluate the requirement's complexity. If a story has no optional fields and no logical error paths, do not force redundant tests. Aim for high-fidelity coverage without over-engineering.

**Example Structure:**
```text
docs/tests/
├── auth/
│   ├── login-mss.md
│   ├── login-optional-fields.md
│   └── login-invalid-credentials.md
└── collections/
    ├── create-collection-mss.md
    └── create-collection-no-name.md
```

## 2. Granular Traceability

The `Test script` field must provide a direct link to the automated execution point. Simply linking to the file is insufficient if the file contains multiple tests.

- **Requirement**: Use the format `[file_name](file_path)#test_name`.
- **Example**: `Test script: [auth-settings.spec.ts](file:///tests/e2e/regression/auth-settings.spec.ts)#AUTH-US02: User Login`

## 3. Structure & Fields

When asked to document a test case in TDD format, you must generate a markdown document with the following fields:

- **title**: Informative, unique, and self-explanatory. Include requirement reference, test suite ID, and classification (MSS, EXT, ERR).
- **description**: A concise overview of the test script's purpose.
- **test_suite**: The organizational group (Feature/Epic name).
- **Covered requirement**: The requirement, User Story, or AC reference being validated.
- **preconditions**: System state required before execution. **Format as a lettered list: A), B), C), etc.**
- **steps**: A markdown table with columns: `Step`, `Action`, and `Expected result`.
- **execution_type**: Usually `Automated`.
- **design_status**: `Draft`, `Ready`, or `Obsolete`.
- **test_engineer**: Identifier of the engineer/agent.
- **test_level**: Priority/Level (1-5).
- **jira**: Relevant Jira ticket ID.
- **Test script**: The granular link to the code (File + Test Name).

## 4. Example Template

```markdown
title: [AUTH-US02] MSS: User Login
description: Validates end-to-end UI behavior for "User Login" in epic "Authentication & Settings".
test_suite: Authentication & Settings
Covered requirement: AUTH-US02
preconditions:
A) Test database is seeded with fixtures.
B) Application is running.
steps:
| Step | Action | Expected result |
|---|---|---|
| 1 | Navigate to login page | Page renders |
| 2 | Enter credentials | Login successful |
execution_type: Automated
design_status: Ready
test_engineer: Antigravity
test_level: 1
jira: N/A
Test script: [auth-settings.spec.ts](file:///tests/e2e/regression/auth-settings.spec.ts)#AUTH-US02: User Login
```

## 5. Architectural Compliance

When documenting a test, the `Test script` MUST point to code that follows the **Triad Architecture** (Fixtures + POM + Stateless Helpers). 
- Preconditions in the document should reflect the **Fixtures** used (e.g., "Precondition: A) AuthenticatedPage fixture is active").
- Steps should reflect the high-level **Page Object** actions, not low-level clicks.
