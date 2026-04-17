---
name: playwright-installer-vscode-codex
description: Editor-setup skill for Playwright plus OpenAI Codex in Visual Studio Code. Use when Codex needs to help configure a practical VS Code environment for Playwright authoring, execution, debugging, and local skill usage.
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

# VS Code + Codex Setup

Use this skill when the user wants a working Playwright workflow in Visual Studio Code with Codex-style assistance.

## Setup Workflow

1. Confirm Node.js, npm, and VS Code are installed.
2. Initialize or inspect the Playwright project.
3. Configure the editor extensions or agent workflow the user actually has available.
4. Verify the environment can run Playwright tests locally.
5. Point the user to the relevant skills in this repository for ongoing work.

## Output Contract

Provide:

- prerequisites,
- setup steps,
- verification commands,
- any editor-specific caveats,
- the next recommended skill or guide after setup.