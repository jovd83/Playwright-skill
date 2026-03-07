---
name: playwright-documentation-root-cause
description: A skill to perform root cause analysis on failed test runs and generate developer-friendly diagnostics.
---

# Root Cause Analysis Documentation

This skill accelerates debugging by automatically triaging test failures.

## Action
When requested to analyze a failure:
1. Read the Playwright trace, console outputs, and failure logs.
2. Determine: "Is it the test or a bug?"
   - **Flaky Test:** E.g., a timeout waiting for a network request, or a brittle selector.
   - **True Bug:** The UI behavior changed, an API responded with a 500, or a feature is broken.
3. Generate a Root Cause Report for the human-in-the-loop:
   - **Test Name:** Which test failed.
   - **The Error:** The literal error from Playwright.
   - **Triage Decision:** Bug OR Flaky Test.
   - **Evidence:** Snippets of the trace or DOM that prove the decision.
   - **Proposed Fix:** What should be done to fix the test or the application.
