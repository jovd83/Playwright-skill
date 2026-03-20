---
name: playwright-documentation-plaintext
description: Legacy Playwright-specific alias for plain-text case formatting. Prefer the standalone `test-artifact-export-skill` skill for lightweight narrative case output, and use this only when Playwright-local conventions must be preserved explicitly.
---

# Playwright Plain-Text Documentation

Use this skill for low-overhead scenario documentation.

## Output Contract

For each scenario, capture:

1. the goal,
2. the relevant setup or preconditions,
3. the main execution flow,
4. the expected outcome,
5. any requirement reference or open question that matters.

Output can be a short paragraph or a flat bullet list, whichever is clearer for the material.

## Writing Rules

- Keep the sequence easy to follow.
- Prefer user intent and expected behavior over implementation detail.
- Make assumptions visible instead of hiding them in prose.
- Do not add formal structure unless the user specifically wants TDD or BDD.
