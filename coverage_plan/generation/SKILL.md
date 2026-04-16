---
name: playwright-coverage-plan-generation
description: Coverage-planning skill for Playwright work. Use when Codex needs to turn confirmed requirements into a structured, risk-aware Playwright coverage plan with scenarios, execution types, priorities, and traceability.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: coverage-planning, playwright-coverage-planning
  dispatcher-accepted-intents: plan_playwright_coverage, generate_ui_test_coverage_plan
  dispatcher-input-artifacts: analysis_baseline, confirmed_requirements, repo_context, scope_constraints
  dispatcher-output-artifacts: coverage_plan, scenario_matrix, approval_request
  dispatcher-stack-tags: playwright, coverage-planning, ui-testing
  dispatcher-risk: medium
  dispatcher-writes-files: false
---

# Playwright Coverage Plan Generation

Use this skill after the requirements are clear enough to plan against.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

## Prerequisites

- Start from confirmed requirements or a clearly labeled analysis baseline.
- If major assumptions remain, keep them visible in the plan instead of burying them.

## Planning Rules

- Aim for meaningful functional completeness, not mechanical scenario inflation.
- Cover the paths that change confidence: core success paths, important variations, failure handling, boundary conditions, and permissions or role differences when relevant.
- Avoid duplicate scenarios that test the same risk with different wording.
- Choose the lowest-cost execution type that still validates the behavior well.

## Output Contract

Produce a coverage plan table like this:

| Priority | Requirement ID | Scenario | Coverage Type | Execution Type | Risk Covered | Notes |
|---|---|---|---|---|---|---|

Use `Coverage Type` values such as `happy-path`, `variation`, `negative`, `edge`, or `resilience` when helpful.

## Execution-Type Guidance

- `UI`: use for end-user behavior, visual flow, or browser-only interactions.
- `API`: use when the behavior can be validated more directly and more cheaply through service calls.
- `Component`: use for isolated UI states or highly focused component behavior.
- Mixed strategies are valid when one requirement needs more than one confidence layer.

## Scope Control

- High-value or logic-heavy features usually need more than one scenario.
- Simple static content often needs only one direct verification.
- Do not omit important unhappy paths just to keep the plan short.
- Do not add low-signal permutations just to make the plan look comprehensive.

## Next Step

Use dispatcher intent `review_playwright_coverage_plan` when explicit review or sign-off is needed before implementation or documentation.

If dispatcher routing is unavailable, use [../review/SKILL.md](../review/SKILL.md).
