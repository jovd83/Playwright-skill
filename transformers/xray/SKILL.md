---
name: playwright-transformer-xray
description: A skill to transform natural language test cases into Xray compatible import formats (JSON/CSV).
---

# Transforming Test Cases to Xray

This skill adapts standard documentation to the specific JSON structure required by Jira Xray.

## Action
When requested:
1. Create a JSON payload with `testtype` set to "Manual" or "Cucumber" and wrapped inside a `tests` array.
2. For Manual tests, convert TDD actions/expected results into Xray's `steps` array (mapping to `action`, `data`, and `result` fields).
3. Connect any Requirement IDs to the Jira Issue Links field.
4. Output the result to `xray_import.json`.
