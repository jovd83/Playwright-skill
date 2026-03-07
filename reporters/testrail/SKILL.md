---
name: playwright-reporter-testrail
description: A skill to use TestRail APIs to report Playwright test execution results.
---

# TestRail API Reporter

This skill allows the agent to report test automation results back to TestRail using the `@testrail-API` integration.

## Action
When reporting results:
1. Ask the user for their TestRail URL and API key.
2. Install the `playwright-testrail-reporter` or `@zealteam/testrail-reporter` library via npm.
3. Configure the reporter in `playwright.config.ts` making sure all environment variables are correctly mapped.
4. Match local tags (`C12345`) to the Case IDs.
5. Use the reporter plugin to push the latest pass/fail/skip metrics directly using the `add_results_for_cases` API endpoint under the hood.
