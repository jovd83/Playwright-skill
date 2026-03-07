---
name: playwright-transformer-testlink
description: A skill to transform natural language test cases (TDD, BDD, Plain Text) into TestLink compatible import formats (XML/CSV).
---

# Transforming Test Cases to TestLink

This skill guides the process of serializing human-readable test documentation into TestLink's required XML structure for bulk importing test suites and test cases.

## Action
When asked to transform test cases to TestLink format:
1. Parse the Natural Language documentation (TDD, BDD, etc.).
2. Generate an XML output mapping conforming to TestLink Document structure:
   - Root node -> `<testcases>`
   - Individual test -> `<testcase name="...">`
   - `Title` -> `<summary>` or `<name>`
   - `Preconditions` -> `<preconditions>`
   - `Actions` -> `<steps><step><actions>`
   - `Expected Results` -> `<steps><step><expectedresults>`
3. Output the raw XML inside a `testlink_import.xml` file or present it to the user.
