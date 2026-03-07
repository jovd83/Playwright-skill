---
name: playwright-reporting-stakeholder
description: A skill to draft human-readable, high-level test execution reports for non-technical stakeholders.
---

# Stakeholder Execution Report

This skill is designed to take raw test execution data and turn it into a digestible summary for product managers and business stakeholders.

## Action
When requested to generate a stakeholder report:
1. Read the Playwright HTML or JSON report.
2. Draft a Markdown or PDF document outlining:
   - **Executive Summary:** Overall health of the release (pass % vs fail %).
   - **Features Tested:** A bulleted list of functional areas covered by the test suite.
   - **Known Issues:** A layman's description of the tests that failed, and the actual business impact (e.g., "Users currently cannot reset their password").
3. Present the drafted report to the user.
