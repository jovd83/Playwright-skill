---
name: playwright-mapper-xray
description: Test-management mapping skill for Xray. Use when Codex needs to apply authoritative Xray test keys or issue IDs back into local Playwright docs, tags, or annotations for reliable traceability and reporting.
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

# Xray Mapper

Use this skill after Xray keys exist and the local repository needs to reflect them.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

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
