---
name: playwright-mapper-xray
description: Test-management mapping skill for Xray. Use when Codex needs to apply authoritative Xray test keys or issue IDs back into local Playwright docs, tags, or annotations for reliable traceability and reporting.
---

# Xray Mapper

Use this skill after Xray keys exist and the local repository needs to reflect them.

## Inputs

- an authoritative mapping from local scenarios to Xray keys,
- the target docs and automation files,
- the repository convention for tags, annotations, or markdown references.

## Output Contract

Produce:

- updated local traceability references,
- a summary of which Xray keys were applied,
- any unresolved matches or conflicts.

## Guardrails

- Do not invent Jira or Xray identifiers.
- Prefer the repository's existing annotation style when one already exists.
