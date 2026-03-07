---
name: playwright-reporter-xray
description: A skill to use Xray APIs to report Playwright test execution results.
---

# Xray API Reporter

This skill handles importing execution results to Jira Xray.

## Action
When requested:
1. Ask the user for Jira Credentials (API token).
2. Install the `@xray-app/playwright-junit-reporter` or `playwright-xray-helper` npm library.
3. Configure the `playwright.config.ts` to output enriched JUnit or JSON.
4. Submit the results to the Xray `/import/execution` REST endpoint using the custom reporter built-in uploading logic or curl.
5. Verify the Jira issue was updated securely, and report back the Execution Issue ID.
