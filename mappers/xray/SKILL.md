---
name: playwright-mapper-xray
description: A skill to map Xray unique IDs back to the local test documentation.
---

# Xray Mapper

After Xray ingestion, JSON/CSV tests receive unique Issue IDs or Test Keys.

## Action
When requested:
1. Obtain the Jira Test Keys for the uploaded tests from the user.
2. Link the Xray ID into the markdown documentation `Covers Xray ID: XRAY-42`.
3. Link the test in Playwright using standard Xray tags or annotations for JUnit: `test('@XRAY-42 verify ...', async () => {})` or inside the test logic: `test.info().annotations.push({ type: 'test_key', description: 'XRAY-42' });`
