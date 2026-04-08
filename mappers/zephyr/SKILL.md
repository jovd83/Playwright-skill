---
name: playwright-mapper-zephyr
description: Test-management mapping skill for Zephyr Scale. Use when Codex needs to apply authoritative Zephyr test keys back into local Playwright docs, titles, or annotations so execution and planning artifacts stay aligned.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: test-management-mapping, playwright-test-management-mapping
  dispatcher-accepted-intents: map_playwright_test_management_ids
  dispatcher-input-artifacts: test_management_ids, local_artifacts, repo_context
  dispatcher-output-artifacts: mapped_traceability_artifacts, mapping_report
  dispatcher-stack-tags: playwright, mapping, test-management
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# Zephyr Mapper

Use this skill after Zephyr keys exist and the local repository needs to reflect them.

## Inputs

- an authoritative mapping from local scenarios to Zephyr keys,
- the target docs and automation files,
- the repository convention for where those keys belong.

## Output Contract

Produce:

- updated local traceability references,
- a summary of which Zephyr keys were applied,
- any unresolved or conflicting mappings.

## Guardrails

- Do not invent IDs.
- Preserve existing naming or tagging conventions unless the user asks to normalize them.
