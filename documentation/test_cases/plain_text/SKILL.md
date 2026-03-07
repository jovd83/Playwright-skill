---
name: playwright-documentation-plaintext
description: A skill to document Playwright test cases in a simple, unformatted plain text style.
---

# Documenting Test Cases: Plain Text format

This skill provides a simple, low-overhead way to document test cases without strict formal structures like TDD or BDD. It is best used for rapid prototyping or informal documentation.

## Structure

When asked to document a test case in plain text format, you must generate a natural language paragraph or a bulleted list describing the flow.

### Guidelines
1. **Clarity**: State the goal of the test clearly in the first sentence.
2. **Context**: Mention any setup required.
3. **Execution**: Describe what happens in a logical sequence.
4. **Outcome**: State what should happen at the end.

### Example

*Test: Login failure*
*To test a failed login, we first need to make sure the app is loaded and the user is on the login screen. The user types in a bad username like "bad@email.com" and a bad password. When they hit submit, the app shouldn't log them in. Instead, it should show a red banner saying "Login failed". Make sure this covers requirement US-101.*

## Usage
Produce this documentation in a simple `.txt` or `.md` file as requested by the user. This format is lightweight and intended for quick human consumption.
