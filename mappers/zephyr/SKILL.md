---
name: playwright-mapper-zephyr
description: Test-management mapping skill for Zephyr Scale. Use when Codex needs to apply authoritative Zephyr test keys back into local Playwright docs, titles, or annotations so execution and planning artifacts stay aligned.
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
