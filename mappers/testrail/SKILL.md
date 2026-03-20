---
name: playwright-mapper-testrail
description: Test-management mapping skill for TestRail. Use when Codex needs to apply authoritative TestRail case IDs back into local Playwright docs, titles, or annotations so automation can be traced or reported accurately.
---

# TestRail Mapper

Use this skill after TestRail case IDs exist and the local repository needs to reflect them.

## Inputs

- an authoritative mapping from local scenarios to TestRail case IDs,
- the target markdown and automation files,
- the repository convention for IDs in titles, tags, or annotations.

## Output Contract

Produce:

- updated local docs or code references,
- a summary of which IDs were applied where,
- any ambiguous or conflicting mappings that were not applied automatically.

## Guardrails

- Do not invent IDs.
- Preserve existing conventions such as tags or title prefixes if the suite already uses them.
