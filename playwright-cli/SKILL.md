---
name: playwright-cli
description: Browser-automation skill for terminal-driven Playwright work. Use when Codex needs to navigate websites, inspect pages, interact with forms, capture screenshots or traces, manage browser sessions, mock requests, or generate test code through a local `playwright-cli` workflow instead of writing a full test first.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: browser-automation-cli, playwright-cli-automation
  dispatcher-accepted-intents: drive_playwright_browser_cli
  dispatcher-input-artifacts: browser_task, target_url, automation_constraints
  dispatcher-output-artifacts: browser_run_artifact, cli_workflow, generated_steps
  dispatcher-stack-tags: playwright, cli, browser-automation
  dispatcher-risk: medium
  dispatcher-writes-files: true
---

# Playwright CLI

Use this skill when terminal-driven browser automation is the fastest path.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

## Assumptions

- A local `playwright-cli` installation is available.
- If command names differ by version, inspect local help output before assuming an exact subcommand shape.

## Operating Rules

1. Snapshot or inspect the page before interacting with referenced elements.
2. Prefer deterministic session naming for parallel or long-running work.
3. Save and restore auth state deliberately when login is expensive.
4. Capture traces before reproducing a failure, not after.
5. Drop into custom code only when the built-in command surface is not enough.

## Command Families

| Need | Guide |
|---|---|
| Basic browser interaction | [core-commands.md](core-commands.md) |
| Request interception and mocking | [request-mocking.md](request-mocking.md) |
| Custom Playwright API execution | [running-custom-code.md](running-custom-code.md) |
| Session and storage management | [session-management.md](session-management.md), [storage-and-auth.md](storage-and-auth.md) |
| Test generation | [test-generation.md](test-generation.md) |
| Tracing and debugging | [tracing-and-debugging.md](tracing-and-debugging.md) |
| Media capture | [screenshots-and-media.md](screenshots-and-media.md) |
| Device and environment emulation | [device-emulation.md](device-emulation.md) |
| Multi-step workflows | [advanced-workflows.md](advanced-workflows.md) |
