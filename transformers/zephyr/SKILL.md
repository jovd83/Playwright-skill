---
name: playwright-transformer-zephyr
description: A skill to transform natural language test cases into Zephyr Scale compatible import formats (JSON/CSV).
---

# Transforming Test Cases to Zephyr

This skill handles converting abstract step definitions into a Zephyr Scale import format.

## Action
When asked to transform test cases to Zephyr format:
1. Extract Steps and Expected outcomes.
2. Structure the data according to the Zephyr Scale JSON schema (for REST API) or Zephyr Test case CSV import template.
   - For CSV, map to: `Name`, `Objective`, `Precondition`, `Test Script (Step-by-Step)`, `Test Script (Expected Result)`.
   - `Title` -> `Name`
   - `Summary` -> `Objective`
3. Output the result into a `zephyr_import.json` or `zephyr_import.csv` file.
