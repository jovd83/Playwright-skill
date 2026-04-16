---
name: playwright-orchestrator
description: Central entrypoint for broad or ambiguous Playwright requests. Use when Codex needs to classify the user's testing goal, choose the right Playwright subskill, and move from intent to implementation, planning, documentation, execution, or reporting without unnecessary menu-driven back-and-forth.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: playwright-orchestration, playwright-routing
  dispatcher-accepted-intents: route_playwright_work, orchestrate_playwright_task
  dispatcher-input-artifacts: user_request, repo_context, requirements, failure_output
  dispatcher-output-artifacts: routing_decision, routing_request, execution_plan
  dispatcher-stack-tags: playwright, orchestration, ui-testing
  dispatcher-risk: medium
  dispatcher-writes-files: false
---

# Playwright Orchestrator

Use this skill when the user asks for Playwright help but the exact workflow is not yet obvious. Its job is to classify the task, route to the right subskill, and keep the work moving.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

## Routing Principles

- Infer the task type when the user already gave enough context.
- Ask a clarifying question only when the answer would materially change the artifact, scope, or next tool.
- Do not stop for a menu when the user already asked for a concrete deliverable.
- Prefer the smallest capable subskill instead of loading the whole pack.

## Route by Intent

| If the user wants to... | Route to... |
|---|---|
| write, fix, or review Playwright tests | [../core/SKILL.md](../core/SKILL.md) |
| choose between fixtures, POMs, and helpers | [../pom/SKILL.md](../pom/SKILL.md) |
| set up or debug CI execution | [../ci/SKILL.md](../ci/SKILL.md) |
| migrate from Cypress or Selenium | [../migration/SKILL.md](../migration/SKILL.md) |
| drive a browser from the terminal | [../playwright-cli/SKILL.md](../playwright-cli/SKILL.md) |
| derive requirements from tickets or specs | [../analysis/SKILL.md](../analysis/SKILL.md) |
| produce or refine a coverage plan | [../coverage_plan/generation/SKILL.md](../coverage_plan/generation/SKILL.md) and [../coverage_plan/review/SKILL.md](../coverage_plan/review/SKILL.md) |
| write test documentation or convert case formats | dispatch `render_test_artifact` through `skill-dispatcher`, or fall back to `C:\projects\skills\test-artifact-export-skill\SKILL.md` |
| investigate failures | [../documentation/root_cause/SKILL.md](../documentation/root_cause/SKILL.md) |
| create handoff or resume-state artifacts | [../documentation/handover/SKILL.md](../documentation/handover/SKILL.md) and [../documentation/session-state/SKILL.md](../documentation/session-state/SKILL.md) |
| export test cases to external test-management systems | dispatch `render_test_artifact` through `skill-dispatcher`, or fall back to `C:\projects\skills\test-artifact-export-skill\SKILL.md` |
| report execution to external test-management systems | the relevant [../mappers/](../mappers/), or [../reporters/](../reporters/) subskill |

## Execution Contract

After routing, do the work. Do not just announce the destination skill.

When helpful, state:

1. the inferred task type,
2. the subskill you are using,
3. any high-impact assumption,
4. the artifact you are about to produce.

## Shared Guardrails

- Prefer web-first assertions and resilient, user-facing locators.
- Do not write placeholder tests or claim implementation is complete when it is blocked.
- Keep setup and state in fixtures, UI behavior in page objects when repetition or complexity justifies them, and helpers stateless.
- Mock third-party dependencies selectively; do not mock away the system under test by default.
- Keep planning and documentation traceable to requirements and executable automation when those artifacts exist.

## Escalation Rules

- If the task is underspecified but low risk, make a reasonable assumption and state it.
- If the task affects scope, cost, or long-lived structure, pause and get the missing decision.
- If multiple subskills are required, use them in sequence and keep the handoff between them explicit.
- Treat direct sibling-skill paths as a compatibility fallback when dispatcher routing is unavailable.
