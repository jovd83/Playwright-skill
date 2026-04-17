---
name: playwright-installer-intellij-junie
description: Editor-setup skill for Playwright plus Junie in IntelliJ IDEA. Use when Codex needs to help configure an IntelliJ-based Playwright workflow with the Junie assistant and verify the environment is ready for authoring and running tests.
metadata:
  author: jovd83
  version: 2.0.0
  dispatcher-category: testing
  dispatcher-capabilities: editor-setup, playwright-editor-setup
  dispatcher-accepted-intents: setup_playwright_editor
  dispatcher-input-artifacts: editor_choice, repo_context, local_environment
  dispatcher-output-artifacts: editor_setup_steps, configuration_guidance
  dispatcher-stack-tags: playwright, setup, editor
  dispatcher-risk: low
  dispatcher-writes-files: false
---

## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `./log-dispatch.cmd --skill <skill_name> --intent <intent> --reason <reason>` (or `./log-dispatch.sh` on Linux)

# IntelliJ + Junie Setup

Use this skill when the user wants a working Playwright workflow in IntelliJ IDEA with Junie.

## Setup Workflow

1. Confirm Node.js, npm, and IntelliJ are installed.
2. Initialize or inspect the Playwright project.
3. Verify the Junie plugin or assistant workflow is available and authenticated as needed.
4. Confirm Playwright tests can run and debug locally.
5. Point the user to the relevant skills in this repository for ongoing work.

## Output Contract

Provide:

- prerequisites,
- setup steps,
- verification commands,
- any IDE-specific caveats,
- the next recommended skill or guide after setup.