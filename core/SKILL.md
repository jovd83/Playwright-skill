---
name: playwright-core
description: Core Playwright implementation skill for resilient test authoring and debugging. Use when Codex needs practical Playwright guidance for locators, assertions, fixtures, authentication, network behavior, API testing, component testing, debugging, framework-specific recipes, or broader test architecture decisions.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: ui-automation, playwright-core, playwright-implementation
  dispatcher-accepted-intents: implement_ui_confirmation_test, debug_playwright_test, review_playwright_test
  dispatcher-input-artifacts: repo_context, requirements, failing_ui_scenario, existing_playwright_suite
  dispatcher-output-artifacts: playwright_test, implementation_guidance, fix_plan
  dispatcher-stack-tags: playwright, ui-testing, implementation
  dispatcher-risk: high
  dispatcher-writes-files: true
---

# Playwright Core

Use this skill for day-to-day Playwright implementation work. It is the foundation of the pack and should be the default path when the user wants tests written, fixed, or reviewed.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

## Core Standards

1. Prefer `getByRole()` and other user-facing locators over brittle selectors.
2. Prefer web-first assertions over manual sleeps or ad hoc polling.
3. Keep tests isolated and independent of execution order.
4. Use `baseURL`, fixtures, and reusable setup instead of hardcoded environment drift.
5. Mock external dependencies selectively; do not mask the system under test without a reason.
6. Choose the lightest test type that still validates the real risk.

## Read by Need

| Need | Guide |
|---|---|
| Locators and selector strategy | [locators.md](locators.md), [locator-strategy.md](locator-strategy.md), [locator-resilience.md](locator-resilience.md) |
| Assertions, waiting, and async behavior | [assertions-and-waiting.md](assertions-and-waiting.md), [debugging.md](debugging.md), [flaky-tests.md](flaky-tests.md) |
| Test structure and data | [test-organization.md](test-organization.md), [test-architecture.md](test-architecture.md), [fixtures-and-hooks.md](fixtures-and-hooks.md), [test-data-management.md](test-data-management.md) |
| Authentication and browser state | [authentication.md](authentication.md), [auth-flows.md](auth-flows.md) |
| API and network behavior | [api-testing.md](api-testing.md), [network-mocking.md](network-mocking.md), [when-to-mock.md](when-to-mock.md), [api-handler-hardening.md](api-handler-hardening.md) |
| UI capability areas | [forms-and-validation.md](forms-and-validation.md), [crud-testing.md](crud-testing.md), [file-upload-download.md](file-upload-download.md), [drag-and-drop.md](drag-and-drop.md), [search-and-filter.md](search-and-filter.md) |
| Reliability and diagnostics | [common-pitfalls.md](common-pitfalls.md), [error-index.md](error-index.md), [error-and-edge-cases.md](error-and-edge-cases.md), [stability-diagnostics.md](stability-diagnostics.md), [preflight.md](preflight.md) |
| Specialized environments | [mobile-and-responsive.md](mobile-and-responsive.md), [component-testing.md](component-testing.md), [browser-apis.md](browser-apis.md), [service-workers-and-pwa.md](service-workers-and-pwa.md), [electron-testing.md](electron-testing.md) |
| Framework recipes | [react.md](react.md), [nextjs.md](nextjs.md), [vue.md](vue.md), [angular.md](angular.md) |

## Scope

- Use this skill for implementation guidance and debugging patterns.
- Move to [../pom/SKILL.md](../pom/SKILL.md) when the main problem is test architecture ownership.
- Move to [../ci/SKILL.md](../ci/SKILL.md) when the main problem is pipeline execution.
