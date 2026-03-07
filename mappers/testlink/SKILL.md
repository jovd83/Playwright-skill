---
name: playwright-mapper-testlink
description: A skill to map TestLink unique IDs back to the local test documentation.
---

# TestLink Mapper

After uploading test cases into TestLink, the platform generates unique External Test Case IDs (e.g., `TC-101`).

## Action
When requested to map TestLink IDs:
1. Ask the user for the mapping list (Test Name -> TestLink ID).
2. Scan the local test documentation and Playwright automation code (`.spec.ts` files).
3. Annotate the test names by adding the ID between brackets `[ ]` at the beginning of the test name.
   - Example TDD: `[TC-101] Verify user login...`
   - Example Playwright: `test('[TC-101] Verify user login...', async () => {})`
