# Playwright Agent Skills

[![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)](CHANGELOG.md) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Validate Skills](https://github.com/jovd83/playwright-skill/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/jovd83/playwright-skill/actions/workflows/validate-skills.yml) [![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/jovd83)

Enterprise-grade Playwright skills for AI coding assistants. This repository packages focused `SKILL.md` entrypoints, reusable reference guides, and deterministic handoff tooling for teams that want Playwright help to feel consistent, installable, and maintainable instead of prompt-fragile.

## What This Repository Is

This is a skill pack, not a single monolithic skill. The repository is organized so an agent can:

- route a broad Playwright request to the right subskill,
- load only the guidance needed for the current task,
- follow shared testing standards across implementation, planning, documentation, and CI,
- optionally use enterprise workflow extensions for handoff, session-state, and test-management integration.

## What This Repository Is Not

- It is not a Playwright test framework template.
- It is not a shared-memory system.
- It does not require every optional pack to be installed together.
- It does not assume every team needs the enterprise workflow extensions.

## Repository Design

The root [`SKILL.md`](SKILL.md) is a navigation layer. It owns routing, package boundaries, and shared standards.

Focused work should move quickly into a specialized subskill:

| Area | Primary path | Use it when |
|---|---|---|
| Core Playwright authoring | [`core/`](core/) | Writing, fixing, or reviewing tests |
| CI/CD | [`ci/`](ci/) | Configuring pipelines, sharding, artifacts, or container runs |
| Page-object architecture | [`pom/`](pom/) | Deciding between fixtures, page objects, and helpers |
| Migration | [`migration/`](migration/) | Moving from Cypress or Selenium |
| CLI browser automation | [`playwright-cli/`](playwright-cli/) | Driving a browser from the terminal without writing a test file |
| Test orchestration | [`orchestrator/`](orchestrator/) | Handling broad or ambiguous testing requests |
| Requirements analysis | [`analysis/`](analysis/) | Turning tickets or specs into testable behaviors |
| Coverage planning | [`coverage_plan/`](coverage_plan/) | Generating, reviewing, or synchronizing coverage plans |
| Documentation | [`documentation/`](documentation/) | Producing TDD, BDD, plain-text, code-doc, root-cause, or handoff artifacts |
| Stakeholder reporting | [`reporting/`](reporting/) | Summarizing outcomes for non-technical audiences |
| Test-management integrations | [`transformers/`](transformers/), [`mappers/`](mappers/), [`reporters/`](reporters/) | Working with TestRail, Xray, Zephyr, or TestLink |
| IDE setup | [`installers/`](installers/) | Installing or aligning editor-specific workflows |

## Architecture Boundaries

This repository keeps three concerns separate:

| Concern | Responsibility | In scope here |
|---|---|---|
| Runtime execution | Solve the current Playwright task | Yes |
| Project-local persistence | Store repo-local plans, handovers, and resume state | Yes, in `documentation/` workflows |
| Shared cross-agent memory | Reuse durable knowledge across repos or teams | No, integrate an external shared-memory skill if needed |

That separation is intentional. Runtime notes should not silently become persistent artifacts, and project-local documentation should not silently become shared organizational memory.

## Installation

Install the full pack:

```bash
npx skills add jovd83/playwright-skill
```

Install focused packs when you only need part of the repository:

```bash
npx skills add jovd83/playwright-skill/core
npx skills add jovd83/playwright-skill/ci
npx skills add jovd83/playwright-skill/pom
npx skills add jovd83/playwright-skill/playwright-cli
npx skills add jovd83/playwright-skill/orchestrator
npx skills add jovd83/playwright-skill/analysis
npx skills add jovd83/playwright-skill/coverage_plan
npx skills add jovd83/playwright-skill/documentation
npx skills add jovd83/playwright-skill/reporters
npx skills add jovd83/playwright-skill/mappers
npx skills add jovd83/playwright-skill/transformers
```

Manual installation also works: clone the repository and place the desired skill folders in the directory your agent platform uses for local skills.

## Core Standards

Across the pack, the default stance is:

- prefer user-facing locators and web-first assertions,
- avoid placeholder tests and fake success claims,
- keep state in fixtures and keep helpers stateless,
- use page objects when repetition or complexity justifies the abstraction,
- keep planning, documentation, and executable tests traceable when those artifacts exist.

These standards are deliberately opinionated. The goal is not theoretical purity; it is reliable outcomes under real delivery pressure.

## Optional Enterprise Workflows

Most Playwright users will care primarily about `core/`, `ci/`, `pom/`, `migration/`, and `playwright-cli/`.

The following areas are optional extensions:

- `analysis/` and `coverage_plan/` for requirements-driven planning
- `documentation/` for test-case artifacts, code documentation, root-cause reports, handovers, and live session-state
- `transformers/`, `mappers/`, and `reporters/` for enterprise test-management systems
- `installers/` and `reporting/` for environment-specific setup and stakeholder communication

See [`reports/skill-inventory.md`](reports/skill-inventory.md) for a generated inventory of every skill, its area, and metadata coverage.

README sections and skill descriptions call these optional where relevant so adopters can separate the core pack from the broader ecosystem.

## Validation

Run the repository validator before publishing or opening a pull request:

```bash
python scripts/validate_skill_repo.py
```

Regenerate the inventory report after adding, renaming, or reorganizing skills:

```bash
python scripts/generate_skill_inventory.py
```

When you change handoff or session-state tooling, also run:

```bash
python documentation/shared/scripts/run_handoff_ci_checks.py --format text
```

The repository includes GitHub Actions validation for repo-wide skill health, inventory freshness, and the handoff workflow tooling.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for repository conventions, validation expectations, and guidance for editing or adding skills without bloating the package.

## Upstream Credit

This repository builds on the upstream Playwright skill foundation originally published by [testdino-hq](https://github.com/testdino-hq/playwright-skill) under the MIT license. This version expands that base into a more structured, multi-skill package with stronger routing, validation, packaging, and enterprise workflow support.

## License

[MIT](LICENSE)
