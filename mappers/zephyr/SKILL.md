---
name: playwright-mapper-zephyr
description: A skill to map Zephyr unique IDs back to the local test documentation.
---

# Zephyr Mapper

After uploading to Zephyr Scale, test cases receive unique Jira keys (e.g., `PROJ-T123`).

## Action
When requested:
1. Request the exported mapping of Names to Zephyr Test Keys from the user.
2. Apply the Zephyr Key (`PROJ-T123`) to the local test documentation.
3. Tag the Playwright code by adding the Zephyr Key at the beginning of the title: `test('PROJ-T123: user login...', async () => {})`
