---
name: playwright-reporter-testlink
description: A skill to use TestLink APIs to report Playwright test execution results.
---

# TestLink API Reporter

This skill handles reporting automation execution results back to TestLink.

## Action
When requested to report results to TestLink:
1. Ask the user for their TestLink API Key and URL if not provided. Give instructions on how to set it securely in the environment if needed.
2. Ensure the `testlink-xmlrpc` or `testlink-api-client` library is installed via npm.
3. Read the latest Playwright test results (e.g., from `playwright-report/` or standard out).
4. Use the mapping from the local tests (e.g., `[TC-101]`) to formulate an API request to the TestLink XML-RPC endpoint.
5. Report the execution status (Passed/Failed) and attach logs in case of failure.
