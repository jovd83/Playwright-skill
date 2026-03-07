# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - Unreleased

### Added
- 

### Changed
- 

### Fixed
- 

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
