---
name: playwright-coverage-plan-review
description: A skill to present the generated functional coverage plan to the user and request their explicit approval.
---

# Functional Coverage Plan Review

This skill ensures human-in-the-loop approval of the test planning before any code or documentation is written.

## 1. Present the Plan
Format the generated test scenarios clearly. Use summary blocks or tables to make it easy for the user to review.

## 2. Prompt for Feedback
Explicitly ask the user:
> "Here is the proposed functional coverage plan based on your requirements. 
> 1. Does this seem okay to you?
> 2. Are there any missing scenarios you would like me to add?
> 3. Are there any scenarios you would like to remove or de-prioritize?"

## 3. Iterate
If the user requests changes, go back, modify the plan according to their feedback, and present it again.

## 4. Proceed
Only when the user provides explicit approval ("Yes", "Looks good", "LGTM", etc.), proceed to the documentation or implementation skills (e.g., `documentation/test_cases/*` or writing the Playwright code).
