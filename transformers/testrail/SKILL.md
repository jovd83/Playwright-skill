---
name: playwright-transformer-testrail
description: A skill to transform natural language test cases into TestRail compatible import formats (XML/CSV).
---

# Transforming Test Cases to TestRail

This skill structures test scenarios into the XML or CSV formats compatible with TestRail's import tool.

## Action
When asked to generate TestRail imports:
1. Extract metadata: Sections, Title, Preconditions.
2. Structure the test steps and expected results via TestRail's custom steps template if using CSV (mapping to `Title`, `Preconditions`, `Steps`, `Expected Result`).
3. Save the layout inside `testrail_import.xml` or `testrail_import.csv`.
