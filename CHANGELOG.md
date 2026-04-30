# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2026-04-30

### Changed
- Trim `SKILL.md` frontmatter to fit the 1000-character dispatcher limit (description trim, migrate non-dispatcher fields to body).

## [1.4.0] - 2026-03-19

### Added
- Added `agents/openai.yaml` metadata for the remaining secondary skills across `coverage_plan/auto-sync`, `migration`, `documentation`, `reporting`, `installers`, `transformers`, `mappers`, and `reporters`.
- Added `scripts/generate_skill_inventory.py` plus the generated [`reports/skill-inventory.md`](reports/skill-inventory.md) report to make package coverage and metadata health easy to inspect.

### Changed
- Standardized the remaining secondary skill entrypoints to use clearer trigger wording, tighter scope, and more consistent input/output contracts.
- Expanded repository validation so every skill directory is now expected to carry `agents/openai.yaml`, not just the primary entrypoints.
- Expanded the GitHub validation workflow to check that the generated inventory report stays in sync with the repository contents.

### Fixed
- Fixed the remaining style drift between primary and secondary skill packs so the repository now reads as one coherent package instead of a mix of polished and prototype-era entrypoints.

### Removed
- Removed a large amount of vague or overly tool-specific secondary-skill phrasing that had made the integration packs feel brittle and inconsistent.

## [1.3.0] - 2026-03-19

### Added
- Added repo-wide `agents/openai.yaml` metadata for the root pack and the primary entrypoint skills (`analysis`, `ci`, `core`, `coverage_plan`, `orchestrator`, `playwright-cli`, and `pom`).
- Added `CONTRIBUTING.md` with repository conventions, validation expectations, and contribution guidance focused on progressive disclosure and maintainability.
- Added `scripts/validate_skill_repo.py` to validate skill frontmatter, featured skill metadata, and repo-local markdown links.
- Added `.github/workflows/validate-skills.yml` for repository-wide skill validation in GitHub Actions.

### Changed
- Rewrote the root `SKILL.md` to act as a clean routing layer with explicit package boundaries, memory-model guidance, and a sharper subskill map.
- Rewrote `README.md` to clearly distinguish the core pack from optional enterprise workflows, explain architecture boundaries, and document validation and installation more cleanly.
- Reworked the main user-facing subskills (`orchestrator`, `analysis`, `coverage_plan`, `core`, `ci`, `pom`, `playwright-cli`) to use clearer trigger descriptions, tighter scope, better output contracts, and less brittle interaction patterns.
- Removed unsupported extra frontmatter from `playwright-cli/SKILL.md` to align better with the standard skill shape.
- Corrected the `core/SKILL.md` guide map to reference `api-handler-hardening.md`.

### Fixed
- Fixed root-level and primary-skill packaging inconsistency by making metadata and routing behavior more uniform across the pack.
- Fixed a major maintainability gap where the repository had no general validation path outside the handoff tooling.

### Removed
- Removed duplicated root-level exposition that had previously turned the root skill and README into oversized indexes instead of focused entrypoints.

## [1.2.0] - 2026-03-13

### Added
- New `documentation/session-state/` skill for maintaining a live resume pointer (`CURRENT.md`) during multi-session or multi-operator work.
- New deterministic handoff and session-state generators, validators, templates, troubleshooting guides, and conflict-resolution references.
- Shared handoff/session-state automation scripts for pair generation, validation, reconciliation, updating, summarizing, reporting, readiness checks, history listing, archiving, restoring, auditing, and repair.
- Lease-based coordination for the live handoff pair, including begin-session and end-session wrappers.
- Portable handoff bundle export, import, inspection, signing, verification, trust evaluation, reporting, and restore workflows under `documentation/shared/scripts/`.
- Checked-in trust policy, redaction policy, and CI policy tooling with generators, validators, examples, and repo discovery support.
- Bundle integrity metadata, HMAC signing, SSH signature support, trusted-only import flow, signer revocation handling, and trust profiles for environment or role-based policies.
- Shared smoke-test coverage for the full handoff workflow plus a CI runner and GitHub Actions workflow for bundle/tooling verification.
- OpenAI agent metadata for the new `handover` and `session-state` skills.

### Changed
- Made the `documentation/handover/` skill fully resume-oriented and aligned it with `agentskills.io` naming and progressive-disclosure expectations.
- Standardized handover and session-state documents on the same canonical status model: `not-started`, `in-progress`, `blocked`, `ready-for-review`, `done`.
- Reworked both skills into numbered execution workflows with deterministic documentation-root discovery and explicit conflict-resolution rules.
- Expanded `README.md` and root `SKILL.md` to index the handover and session-state skills as first-class capabilities.
- Hardened portable bundle export with git-context capture, patch-summary fingerprints, redaction policies, and broader secret detection coverage for common provider token formats.
- Expanded trust-policy generation to support named profiles, profile templates, and profile-specific overrides for signer rules, age limits, lease rules, and signature-secret environment variables.
- Expanded CI checks to validate trust, redaction, and CI policy files when present, with opt-in enforcement for repos that require checked-in portable-bundle policy files.

### Fixed
- Corrected the handover skill frontmatter so the skill name matches the folder name and the descriptions use trigger-oriented `Use when...` wording.
- Fixed state drift and cross-link inconsistencies between handover files, `CURRENT.md`, and archived snapshots through deterministic reconciliation and repair tooling.
- Fixed portable bundle path normalization to use forward-slash cross-links consistently across Windows and non-Windows environments.
- Fixed bundle inspection, import, and trust flows to reject tampered, unsigned, revoked, stale, or policy-incompatible artifacts deterministically.
- Fixed multiple secret-redaction gaps by adding built-in detection for Slack, Stripe, OpenAI, Anthropic, Google, Hugging Face, Discord, Mailchimp, SendGrid, Shopify, Twilio, Postman, GitHub, GitLab, npm, JWT, and private-key material patterns.

### Removed
- 

## [1.1.0] - 2026-03-07

### Added
- Expanded specific IDE documentation links (Cursor, VS Code, JetBrains, OpenClaw) in `README.md`.

### Changed
- Softened rigidity of scenario generation instructions in `coverage_plan` and `documentation` skills.
- Replaced mandatory "MSS/EXT/ERR" classification with guidelines for "Functional Completeness" and meaningful variations.
- Removed fixed "at least 3 scenarios" count in BDD documentation to allow for better risk-based coverage.
- Updated descriptive scenario naming requirements in TDD documentation.
- Personalized installation instructions in `README.md` to reference `jovd83`'s fork repository directly.

### Fixed
- 

### Removed
- 

## [1.0.0] - 2026-03-07

### Added
- Core Playwright skills (`core/`, `SKILL.md`) and subskills organization.
- Implementation of Triad Architecture standards (Fixtures, Page Objects, Stateless Helpers) and documentation restricting placeholder assertions.
- Test Automation and TDD documentation structural rules (`documentation/`).
- Automated handovers functionality (`handovers/` directory tracking).
- Workload Distribution Charts components and data definitions for reporting (`reporting/`).
- API Route Hardening generic best practices guidelines (`analysis/` or `core/`).
- Migration tools or documentation for creating Cypress skills (`migration/`).
- IDE documentation links to README (`README.md`).
- `.gitignore` specifically excluding the `requested_improvements/` directory.

### Changed
- Refactored TDD Documentation to enforce feature-based folder organization and granular test linking.

### Removed
- Archived old Playwright tests to make way for new standardization.
