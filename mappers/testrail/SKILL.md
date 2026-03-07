---
name: playwright-mapper-testrail
description: A skill to map TestRail unique IDs back to the local test documentation.
---

# TestRail Mapper

After adding test cases to a TestRail suite, they get assigned an ID (e.g., `C12345`).

## Action
When requested:
1. Ask the user for the TestRail Case ID mappings.
2. Insert the TestRail ID into the markdown test documentation.
3. Integrate the Case ID into the Playwright test titles (which is required by the TestRail reporter plugin): `test('C12345 Verify user login...', async () => {})` or using tags `@C12345`.
