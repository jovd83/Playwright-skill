---
name: playwright-mapper-testlink
description: Test-management mapping skill for TestLink. Use when Codex needs to apply authoritative TestLink case IDs back into local Playwright docs, titles, or annotations so the repository can trace automation to imported TestLink records.
metadata:
  author: jovd83
  version: 2.0.0
  dispatcher-category: testing
  dispatcher-capabilities: test-management-mapping, playwright-test-management-mapping
  dispatcher-accepted-intents: map_playwright_test_management_ids
  dispatcher-input-artifacts: test_management_ids, local_artifacts, repo_context
  dispatcher-output-artifacts: mapped_traceability_artifacts, mapping_report
  dispatcher-stack-tags: playwright, mapping, test-management
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# TestLink Mapper

Use this skill after TestLink has assigned IDs and the local repository needs to reflect them.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

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
