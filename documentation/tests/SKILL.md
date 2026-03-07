---
name: playwright-documentation-tests
description: A skill to add human-readable documentation to existing Playwright tests.
---

# Documenting Existing Tests

This skill helps maintain the readability of the test automation codebase for non-technical users and domain experts.

## Action
When asked to document tests:
1. Scan the specified `.spec.ts` files.
2. For each test block (`test('...', async () => {})`), analyze the Playwright actions.
3. Add a JSDoc block `/** ... */` immediately above the test, explaining what the test does in plain English.
   - Example:
     ```typescript
     /**
      * This test ensures that when a user tries to checkout with an empty cart,
      * they are shown a validation error and prevented from reaching the payment screen.
      */
     test('Empty cart validation', async ({ page }) => { ... })
     ```
