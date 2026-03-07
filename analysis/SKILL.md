---
name: playwright-analysis-requirements
description: A skill to find and analyze requirements (epics, user stories, acceptance criteria) mapping to the current testing scope.
---

# Analysis & Requirements Skill

This skill guides you through the process of establishing the functional requirements baseline before testing begins.

## 1. Information Gathering
- Automatically search the repository context (Markdown files, Jira exports, issue tracking links, `docs/` folders) for the relevant Epics, User Stories, and Acceptance Criteria (AC).
- Alternatively, if the user points you toward a specific document or ticket, read it thoroughly.

## 2. Requirement Extraction
- Summarize the business logic into distinct, testable behaviors.
- Ensure all edge cases mentioned in the AC are included in your analysis.

## 3. User Validation
- Once you have aggregated the requirements, present them back to the user.
- **Action Required**: Ask the user: "Is this summary of the Epic, User Stories, and Acceptance Criteria correct and complete? If not, where should I look for the missing information?"
- **Blocker**: Do *not* proceed to the coverage plan or test authoring until the user confirms the requirements are correct.
