# Playwright Skill Guides

Playwright guides for E2E, API, component, visual, accessibility, and security testing, plus CLI automation. **70+ guides** with TypeScript and JavaScript examples.

## What are Agent Skills?
[Agent Skills](https://github.com/agentskills/agentskills) are a simple, open format for giving AI agents capabilities and expertise. They are essentially folders of instructions, scripts, and resources that agents can discover and use to perform better at specific tasks. Write once, use everywhere!

## Installation Manual

This repository provides Playwright skills designed for AI coding assistants (like OpenAI Codex or Junie). To take full advantage of these skills, you need to import them into your project so your agent can read them.

### Step 1: Base Installation
You can add all the core skills and the orchestrator at once using the `npx skills` command:

```bash
npx skills add jovd83/playwright-skill
```

### Step 2: Customizing Your Setup
If you only need specific functionalities (e.g., just the reporters or just the mappers), you can add individual skill packs:

**Core & CI/CD**
```bash
npx skills add jovd83/playwright-skill/core
npx skills add jovd83/playwright-skill/ci
npx skills add jovd83/playwright-skill/pom
npx skills add jovd83/playwright-skill/migration
npx skills add jovd83/playwright-skill/playwright-cli
```

**Test Management Extensions**
```bash
npx skills add jovd83/playwright-skill/orchestrator
npx skills add jovd83/playwright-skill/analysis
npx skills add jovd83/playwright-skill/coverage_plan
npx skills add jovd83/playwright-skill/documentation
npx skills add jovd83/playwright-skill/transformers
npx skills add jovd83/playwright-skill/mappers
npx skills add jovd83/playwright-skill/reporters
npx skills add jovd83/playwright-skill/reporting
```

Once installed, your AI agent will automatically reference the `SKILL.md` files imported into your workspace when you ask it testing-related questions!

### Manual Installation (Alternative)
If you prefer not to use `npx skills`, you can manually download this repository and place the guides in either a system-wide or IDE-specific skills directory.

**1. Download the Files**
Download or clone this repository to your local machine:
```bash
git clone https://github.com/jovd83/Playwright-skill.git
```

**2. Place the Skills Folder**
Move the `playwright-skill` folder to the appropriate location where your AI assistant looks for custom skills:

- **System-wide (Generic Agents):** Typically placed in a shared directory like `~/.agents/skills/`.
- **For a specific IDE:** Copy the folder into `~/.cursor/skills/`.
  *Note: Check the documentation of your specific AI assistant for the exact directory paths it supports for injecting local skill files. i.e.:*
  - *Google antigravity: https://antigravity.google/docs/skills*
  - *Cursor: https://cursor.dev/docs/skills*
  - *Visual Studio Code: https://code.visualstudio.com/docs/copilot/customization/agent-skills*
  - *JetBrains: https://plugins.jetbrains.com/plugin/29975-agent-skills-manage*
  - *OpenClaw: https://docs.openclaw.ai/tools/skills*

## Skills Overview

| Skill Pack | Guides | What's Covered |
|---|:---:|---|
| **core** | 46 | Locators, assertions, fixtures, auth, API testing, network mocking, visual regression, accessibility, debugging, framework recipes |
| **ci** | 9 | GitHub Actions, GitLab CI, CircleCI, Azure DevOps, Jenkins, Docker, sharding, reporting, coverage |
| **pom** | 2 | Page Object Model patterns, POM vs fixtures vs helpers |
| **migration** | 2 | Migrating from Cypress, migrating from Selenium |
| **playwright-cli** | 11 | CLI browser automation, screenshots, tracing, session management, device emulation |

## Core Skills

The foundation of Playwright testing. These guides cover everything you need to write, debug, and maintain reliable end-to-end tests.

- **Start here** if you're new to Playwright — begin with locators, assertions, and fixtures
- Covers common patterns like authentication, API testing, network mocking, and visual regression
- Includes framework-specific recipes for React, Vue, Angular, and Next.js
- Debugging guides to help you fix flaky tests and common pitfalls

### Writing Tests

| Guide | Description |
|---|---|
| [locators.md](core/locators.md) | Selector strategies — `getByRole`, `getByText`, `getByTestId` |
| [assertions-and-waiting.md](core/assertions-and-waiting.md) | Web-first assertions, auto-retry, waiting patterns |
| [fixtures-and-hooks.md](core/fixtures-and-hooks.md) | `test.extend()`, setup/teardown, worker-scoped fixtures |
| [configuration.md](core/configuration.md) | `playwright.config.ts` — projects, timeouts, reporters, web server |
| [test-organization.md](core/test-organization.md) | File structure, tagging, `test.describe`, test filtering |
| [test-data-management.md](core/test-data-management.md) | Factories, seeding, cleanup strategies |
| [authentication.md](core/authentication.md) | Storage state reuse, multi-role auth, session management |
| [api-testing.md](core/api-testing.md) | REST and GraphQL testing with `request` fixture |
| [network-mocking.md](core/network-mocking.md) | Route interception, HAR replay, response modification |
| [forms-and-validation.md](core/forms-and-validation.md) | Form fills, validation, error states, multi-step wizards |
| [visual-regression.md](core/visual-regression.md) | Screenshot comparison, thresholds, masking dynamic content |
| [accessibility.md](core/accessibility.md) | axe-core integration, ARIA assertions, a11y auditing |
| [component-testing.md](core/component-testing.md) | Mount React/Vue/Svelte components in isolation |
| [mobile-and-responsive.md](core/mobile-and-responsive.md) | Device emulation, viewport testing, touch interactions |
| [search-and-filter.md](core/search-and-filter.md) | Testing search bars, debouncing, and filter combinations |
| [route-behavior.md](core/route-behavior.md) | URL routing, query parameters, navigation |
| [locator-resilience.md](core/locator-resilience.md) | Making locators robust against layout shifts |
| [testability-hooks.md](core/testability-hooks.md) | Exposing internal state specifically for testing |
| [api-handler-hardening.md](core/api-handler-hardening.md) | Unit testing API endpoints directly |
| [contract-first-mocking.md](core/contract-first-mocking.md) | Contract-driven network mocking |

### Debugging & Fixing

| Guide | Description |
|---|---|
| [debugging.md](core/debugging.md) | Trace viewer, `PWDEBUG`, UI mode, headed + slow-mo |
| [error-index.md](core/error-index.md) | Common error messages and how to fix them |
| [flaky-tests.md](core/flaky-tests.md) | Root causes, retry strategies, stabilization patterns |
| [common-pitfalls.md](core/common-pitfalls.md) | Top beginner mistakes and how to avoid them |
| [stability-diagnostics.md](core/stability-diagnostics.md) | Diagnosing execution stability issues |
| [preflight.md](core/preflight.md) | Environment readiness preflight checks |

### Framework Recipes

| Guide | Description |
|---|---|
| [nextjs.md](core/nextjs.md) | App Router + Pages Router testing |
| [react.md](core/react.md) | CRA, Vite, component testing |
| [vue.md](core/vue.md) | Vue 3 / Nuxt testing |
| [angular.md](core/angular.md) | Angular testing patterns |

### Specialized Topics

| Guide | Description |
|---|---|
| [browser-apis.md](core/browser-apis.md) | Geolocation, clipboard, permissions |
| [iframes-and-shadow-dom.md](core/iframes-and-shadow-dom.md) | Cross-frame testing, Shadow DOM piercing |
| [multi-context-and-popups.md](core/multi-context-and-popups.md) | Multi-tab, popups, new windows |
| [websockets-and-realtime.md](core/websockets-and-realtime.md) | WebSocket testing, real-time UI |
| [canvas-and-webgl.md](core/canvas-and-webgl.md) | Canvas testing, visual comparison |
| [electron-testing.md](core/electron-testing.md) | Desktop app testing with Electron |
| [security-testing.md](core/security-testing.md) | XSS, CSRF, header validation |
| [performance-testing.md](core/performance-testing.md) | Core Web Vitals, Lighthouse, benchmarks |
| [clock-and-time-mocking.md](core/clock-and-time-mocking.md) | Fake timers, date mocking |
| [service-workers-and-pwa.md](core/service-workers-and-pwa.md) | PWA testing, offline mode |
| [browser-extensions.md](core/browser-extensions.md) | Extension testing patterns |
| [i18n-and-localization.md](core/i18n-and-localization.md) | Multi-language, RTL, locale testing |

## CI/CD Skills

| Guide | Description |
|---|---|
| [ci-github-actions.md](ci/ci-github-actions.md) | Workflows, caching, artifact uploads |
| [ci-gitlab.md](ci/ci-gitlab.md) | GitLab CI pipelines |
| [ci-other.md](ci/ci-other.md) | CircleCI, Azure DevOps, Jenkins |
| [parallel-and-sharding.md](ci/parallel-and-sharding.md) | Sharding across CI runners |
| [docker-and-containers.md](ci/docker-and-containers.md) | Containerized test execution |
| [reporting-and-artifacts.md](ci/reporting-and-artifacts.md) | HTML reports, traces, screenshots |
| [test-coverage.md](ci/test-coverage.md) | Code coverage collection |
| [global-setup-teardown.md](ci/global-setup-teardown.md) | One-time setup/teardown |
| [projects-and-dependencies.md](ci/projects-and-dependencies.md) | Multi-project config, dependencies |

## Playwright CLI Skills

| Guide | Description |
|---|---|
| [core-commands.md](playwright-cli/core-commands.md) | Open, navigate, click, fill, keyboard, mouse |
| [request-mocking.md](playwright-cli/request-mocking.md) | Route interception, conditional mocks, HAR replay |
| [running-custom-code.md](playwright-cli/running-custom-code.md) | Full Playwright API via `run-code` |
| [session-management.md](playwright-cli/session-management.md) | Named sessions, isolation, persistent profiles |
| [storage-and-auth.md](playwright-cli/storage-and-auth.md) | Cookies, localStorage, auth state save/restore |
| [test-generation.md](playwright-cli/test-generation.md) | Auto-generate test code from CLI interactions |
| [tracing-and-debugging.md](playwright-cli/tracing-and-debugging.md) | Traces, console/network monitoring |
| [screenshots-and-media.md](playwright-cli/screenshots-and-media.md) | Screenshots, video recording, PDF export |
| [device-emulation.md](playwright-cli/device-emulation.md) | Viewport, geolocation, locale, dark mode |
| [advanced-workflows.md](playwright-cli/advanced-workflows.md) | Popups, scraping, accessibility auditing |

## Migration Skills

| Guide | Description |
|---|---|
| [from-cypress.md](migration/from-cypress.md) | Cypress to Playwright migration |
| [from-selenium.md](migration/from-selenium.md) | Selenium/WebDriver to Playwright migration |

## Page Object Model Skills

| Guide | Description |
|---|---|
| [page-object-model.md](pom/page-object-model.md) | POM patterns for Playwright |
| [pom-vs-fixtures-vs-helpers.md](pom/pom-vs-fixtures-vs-helpers.md) | When to use POM vs fixtures vs helpers |

## Skills Documentation

This section provides a detailed index of all AI skills and deep-dive guides. These files are designed to be consumed by AI agents to provide expert-level assistance throughout the testing lifecycle.

### 1. Automation Core (The Foundation)

- **[SKILL.md](core/SKILL.md)**: The primary entry point for the core pack, guiding the agent in setting up a robust, web-first automation foundation.
- **[locators.md](core/locators.md)**: Detailed strategies for the locator hierarchy, prioritizing user-facing roles and test-IDs over fragile CSS selectors.
- **[locator-strategy.md](core/locator-strategy.md)**: Theoretical and practical comparison of different locator methods and when to use them.
- **[assertions-and-waiting.md](core/assertions-and-waiting.md)**: Patterns for auto-retrying assertions, handling asynchronous UI states, and verifying success feedback (toasts).
- **[fixtures-and-hooks.md](core/fixtures-and-hooks.md)**: How to use `test.extend()` to share state and setup logic across tests without using global variables.
- **[configuration.md](core/configuration.md)**: Deep dive into `playwright.config.ts`, covering projects, timeouts, browsers, and reporters.
- **[test-organization.md](core/test-organization.md)**: Guidelines for folder structures, `describe` blocks, tagging, and selective test execution.
- **[test-data-management.md](core/test-data-management.md)**: Strategies for factories, seeding, and cleanup to ensure tests are isolated and repeatable.
- **[test-architecture.md](core/test-architecture.md)**: High-level patterns for choosing between E2E, API, and component tests.
- **[authentication.md](core/authentication.md)**: Strategies for storage state reuse, multi-role auth, and session management to speed up test execution.
- **[auth-flows.md](core/auth-flows.md)**: Step-by-step recipes for different authentication scenarios (OAuth, SAML, basic auth).
- **[api-testing.md](core/api-testing.md)**: Best practices for combining UI and API testing, using Playwright as a REST/GraphQL client.
- **[network-mocking.md](core/network-mocking.md)**: Recipes for route interception, HAR replay, and modifying API responses for edge-case testing.
- **[when-to-mock.md](core/when-to-mock.md)**: Decision framework for choosing between real APIs, mocked responses, and local stubs.
- **[forms-and-validation.md](core/forms-and-validation.md)**: Comprehensive guide for testing complex forms, including multi-step wizards and server-side validation.
- **[crud-testing.md](core/crud-testing.md)**: Patterns for Create, Read, Update, and Delete workflows, ensuring data integrity throughout the lifecycle.
- **[drag-and-drop.md](core/drag-and-drop.md)**: Reliable patterns for testing mouse-driven drag and drop interactions.
- **[file-operations.md](core/file-operations.md)**: Basics of file manipulation, system paths, and temporary data handling in tests.
- **[file-upload-download.md](core/file-upload-download.md)**: Specific recipes for testing file upload fields and verifying downloads.
- **[visual-regression.md](core/visual-regression.md)**: Configuring pixel-perfect comparisons, setting thresholds, and masking dynamic UI elements.
- **[accessibility.md](core/accessibility.md)**: Integrating `axe-core` for automated accessibility audits and ARIA-compliant assertions.
- **[mobile-and-responsive.md](core/mobile-and-responsive.md)**: Testing across viewports, device emulation, and touch interaction simulation.
- **[iframes-and-shadow-dom.md](core/iframes-and-shadow-dom.md)**: Strategies for piercing the Shadow DOM and navigating complex iframe hierarchies.
- **[multi-context-and-popups.md](core/multi-context-and-popups.md)**: Handling multiple browser contexts, tabs, and interacting with new window popups.
- **[multi-user-and-collaboration.md](core/multi-user-and-collaboration.md)**: Patterns for testing real-time collaborative features with multiple browsers in parallel.
- **[websockets-and-realtime.md](core/websockets-and-realtime.md)**: Listening to and asserting on WebSocket messages and real-time UI updates.
- **[browser-apis.md](core/browser-apis.md)**: Testing interactions with Geolocation, Clipboard, Permissions, and Notification APIs.
- **[browser-extensions.md](core/browser-extensions.md)**: Specialized setup for testing Chrome and Firefox browser extensions.
- **[service-workers-and-pwa.md](core/service-workers-and-pwa.md)**: Testing Service Worker registration, offline modes, and PWA installability.
- **[canvas-and-webgl.md](core/canvas-and-webgl.md)**: Advanced techniques for testing Canvas-based applications and WebGL rendering.
- **[electron-testing.md](core/electron-testing.md)**: End-to-end testing for Electron-based desktop applications.
- **[security-testing.md](core/security-testing.md)**: Basic security audits including XSS, CSRF, and header validation tests.
- **[performance-testing.md](core/performance-testing.md)**: Tracking Core Web Vitals, custom timing metrics, and Lighthouse integration.
- **[clock-and-time-mocking.md](core/clock-and-time-mocking.md)**: Using `page.clock` to manipulate time for testing timeouts and scheduled events.
- **[i18n-and-localization.md](core/i18n-and-localization.md)**: Testing multi-language support, RTL layouts, and locale-specific data.
- **[third-party-integrations.md](core/third-party-integrations.md)**: Mocking and testing integrations with external services like Stripe or Firebase.
- **[component-testing.md](core/component-testing.md)**: How to mount React, Vue, or Svelte components in isolation for fast, unit-like UI testing.
- **[react.md](core/react.md)**, **[vue.md](core/vue.md)**, **[angular.md](core/angular.md)**, **[nextjs.md](core/nextjs.md)**: Framework-specific optimization guides.
- **[debugging.md](core/debugging.md)**: Mastering the Trace Viewer, UI Mode, and headed debugging to find the root cause of failures.
- **[error-index.md](core/error-index.md)**: A searchable catalog of Playwright errors and their verified solutions.
- **[error-and-edge-cases.md](core/error-and-edge-cases.md)**: Designing tests for "unhappy paths," including 404s, 500s, and connectivity losses.
- **[flaky-tests.md](core/flaky-tests.md)**: A collection of stabilization patterns to eliminate non-deterministic test failures.
- **[common-pitfalls.md](core/common-pitfalls.md)**: A "hall of fame" of beginner mistakes and the recommended professional alternatives.
- **[search-and-filter.md](core/search-and-filter.md)**: Testing search UI, debouncing, and filter combinations.
- **[route-behavior.md](core/route-behavior.md)**: Handling URL routing, parameters, and navigation.
- **[locator-resilience.md](core/locator-resilience.md)**: Creating resilient tests when DOM structures or content changes.
- **[testability-hooks.md](core/testability-hooks.md)**: Exposing test metadata or internal state dynamically.
- **[api-handler-hardening.md](core/api-handler-hardening.md)**: Unit testing API endpoints directly and rigorous response validation.
- **[stability-diagnostics.md](core/stability-diagnostics.md)**: Diagnostics and tools to identify stability and flaky performance issues locally.
- **[preflight.md](core/preflight.md)**: Pre-test validation scripts for checking environment readiness.
- **[contract-first-mocking.md](core/contract-first-mocking.md)**: Isolating UI behaviors independent of real network state using mock contracts.

### 2. CI/CD & Infrastructure

- **[SKILL.md](ci/SKILL.md)**: The orchestrator for pipeline setup, guiding the agent through sharding and artifact management.
- **[ci-github-actions.md](ci/ci-github-actions.md)**: Optimized YAML examples for GitHub Actions, including caching and matrix execution.
- **[ci-gitlab.md](ci/ci-gitlab.md)**: Implementation guide for GitLab CI/CD pipelines and artifact exposure.
- **[ci-other.md](ci/ci-other.md)**: Configuration patterns for Azure DevOps, Jenkins, and CircleCI.
- **[parallel-and-sharding.md](ci/parallel-and-sharding.md)**: How to scale test execution across multiple runners and merge the resulting reports.
- **[docker-and-containers.md](ci/docker-and-containers.md)**: Running Playwright in Docker for consistent execution across environments.
- **[reporting-and-artifacts.md](ci/reporting-and-artifacts.md)**: Configuring HTML reports, traces, and metadata for team visibility.
- **[test-coverage.md](ci/test-coverage.md)**: Collecting and reporting code coverage (Istanbul/V8) to identify untested logic.
- **[global-setup-teardown.md](ci/global-setup-teardown.md)**: One-time environment preparation (auth, DB seeding) that runs before the entire test suite.
- **[projects-and-dependencies.md](ci/projects-and-dependencies.md)**: Managing multi-project configurations (e.g., Desktop vs. Mobile) and setup dependencies.

### 3. Requirements & Planning

- **[analysis/SKILL.md](analysis/SKILL.md)**: High-level skill for extracting testable requirements from documentation and Jira.
- **[coverage_plan/generation/SKILL.md](coverage_plan/generation/SKILL.md)**: Logic for deriving a functional coverage plan (Happy, Alternative, Negative paths).
- **[coverage_plan/review/SKILL.md](coverage_plan/review/SKILL.md)**: Orchestration for a human-in-the-loop review session of the proposed testing plan.
- **[coverage_plan/auto-sync/SKILL.md](coverage_plan/auto-sync/SKILL.md)**: Keeping plans and traceability in sync with actual runs.

### 4. Test Documentation & Failure Analysis

- **[documentation/test_cases/tdd/SKILL.md](documentation/test_cases/tdd/SKILL.md)**: Mandatory template for Traceability-focused test cases (Title, Requirements, Preconditions, Steps).
- **[documentation/test_cases/bdd/SKILL.md](documentation/test_cases/bdd/SKILL.md)**: Guidance for writing Gherkin-compliant Feature files for Cucumber/BDD workflows.
- **[documentation/test_cases/plain_text/SKILL.md](documentation/test_cases/plain_text/SKILL.md)**: Informal scenario drafting for quick feedback loops.
- **[documentation/tests/SKILL.md](documentation/tests/SKILL.md)**: Automatically adding plain-English JSDoc comments to existing automation code.
- **[documentation/root_cause/SKILL.md](documentation/root_cause/SKILL.md)**: Structured approach to documenting bug investigations and environment resolutions.
- **[documentation/handover/SKILL.md](documentation/handover/SKILL.md)**: Structured handover protocol for documenting actions taken, skills used, and generating a formal handover document.

### 5. Playwright CLI (Manual & Agentic Hub)

- **[SKILL.md](playwright-cli/SKILL.md)**: Central skill for using the CLI to perform rapid, scriptless browser automation.
- **[core-commands.md](playwright-cli/core-commands.md)**: Guide for individual actions (click, fill, navigate) via terminal commands.
- **[session-management.md](playwright-cli/session-management.md)**: Managing persistent storage profiles to bypass login during CLI sessions.
- **[storage-and-auth.md](playwright-cli/storage-and-auth.md)**: Saving and restoring authentication states (cookies/localStorage) from the command line.
- **[test-generation.md](playwright-cli/test-generation.md)**: Using `codegen` to record interactions and transform them into reusable code.
- **[request-mocking.md](playwright-cli/request-mocking.md)**: Route interception and responsive mocking directly from the CLI.
- **[running-custom-code.md](playwright-cli/running-custom-code.md)**: Executing arbitrary JavaScript and Playwright snippets on the fly.
- **[screenshots-and-media.md](playwright-cli/screenshots-and-media.md)**: CLI-based capture of images, videos, and PDFs for reporting.
- **[device-emulation.md](playwright-cli/device-emulation.md)**: Simulating different devices, viewports, and network conditions from the terminal.
- **[tracing-and-debugging.md](playwright-cli/tracing-and-debugging.md)**: Managing traces and using the debugger via CLI.
- **[advanced-workflows.md](playwright-cli/advanced-workflows.md)**: Complex automation scenarios including multi-context and background tasks.

### 6. Migration & Architecture

- **[migration/SKILL.md](migration/SKILL.md)**: Strategy guide for transitioning from legacy frameworks to Playwright.
- **[migration/from-cypress.md](migration/from-cypress.md)**: Command-by-command mapping and architectural differences for Cypress users.
- **[migration/from-selenium.md](migration/from-selenium.md)**: Transition guide for Selenium users, focusing on auto-waiting and locator logic.
- **[pom/SKILL.md](pom/SKILL.md)**: Overview of Page Object Model best practices and maintainability.
- **[pom/page-object-model.md](pom/page-object-model.md)**: Implementation patterns for clean, scalable page objects.
- **[pom/pom-vs-fixtures-vs-helpers.md](pom/pom-vs-fixtures-vs-helpers.md)**: Decision framework for choosing the right architecture pattern for your project.

### 7. Enterprise Integration & Orchestration

- **[orchestrator/SKILL.md](orchestrator/SKILL.md)**: The primary entry point for any testing task, clarifying goals and routing to specialized sub-skills.
- **[reporting/stakeholder/SKILL.md](reporting/stakeholder/SKILL.md)**: Drafting human-readable release summaries for non-technical leadership.
- **[transformers/](transformers/)**: Converters for formatting test scenarios for **Zephyr**, **Xray**, **TestRail**, and **TestLink**.
- **[mappers/](mappers/)**: Syncing unique management tool IDs back into local markdown and automation code.
- **[reporters/](reporters/)**: Publishing test execution results directly to management platforms via REST APIs.
- **[installers/](installers/)**: Platform-specific installation guides for **VS Code (Codex)** and **IntelliJ (Junie)** environments.

## Note

The original guides can be found on [https://github.com/testdino-hq/playwright-skill?tab=readme-ov-file](https://github.com/testdino-hq/playwright-skill?tab=readme-ov-file) under the MIT license. 

A massive **thank you** to the original authors at [testdino-hq](https://github.com/testdino-hq) for providing such an incredible and comprehensive foundation of Playwright knowledge! 

This local version has been heavily adapted and expanded to act as a complete orchestrator-level skill set. The key differences and additions relative to the upstream repository include:
- **Core Expansions:** Added new guides for API handler hardening, contract-first mocking, locator resilience, preflight checks, and stability diagnostics.
- **Coverage & Planning (`coverage_plan/`):** Entirely new subskills for generating coverage plans, human-in-the-loop review generation, and test sync tracking.
- **Formal Documentation (`documentation/`):** Added structures for BDD/TDD traceability, handover generation, and structured root-cause analysis.
- **Test Management Integrations:** Added full suites (Mappers, Reporters, and Transformers) connecting directly to Enterprise systems like **TestLink**, **TestRail**, **Xray**, and **Zephyr**.
- **Orchestration & Tools:** Added an overarching orchestrator skill, stakeholder reporting, request tracking, and IDE-specific installers for VS Code and IntelliJ.


## License

[MIT](LICENSE)
