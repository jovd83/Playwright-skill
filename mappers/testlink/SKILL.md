---
name: playwright-mapper-testlink
description: Test-management mapping skill for TestLink. Use when Codex needs to apply authoritative TestLink case IDs back into local Playwright docs, titles, or annotations so the repository can trace automation to imported TestLink records.
---

# TestLink Mapper

Use this skill after TestLink has assigned IDs and the local repository needs to reflect them.

## Inputs

- an authoritative mapping from local scenario names or paths to TestLink IDs,
- the target markdown and automation files,
- the team convention for where IDs belong in docs or test titles.

## Output Contract

Produce:

- updated local docs or code references,
- a summary of which IDs were applied where,
- any ambiguous matches that still need human confirmation.

## Guardrails

- Do not invent IDs.
- Do not overwrite an existing different ID without calling out the conflict.
- Prefer annotations or title conventions already used by the repository.
