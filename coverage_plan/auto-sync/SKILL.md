---
name: playwright-coverage-matrix-auto-sync
description: Keep requirements and test-traceability documentation in sync as scenarios are added or changed. Maintains anchor links and recalculates coverage stats.
---

# Coverage Matrix Auto-Sync

Use this skill to ensure that your functional coverage plans and traceability documents stay updated as you modify tests or requirements.

## 1. Traceability Maintenance
Whenever a test case is added, removed, or moved:
- **Scan for Anchors**: Look for `[Scenario ID]` anchors in the test documentation.
- **Update Mapping**: Ensure the `TDD` or `BDD` document matches the latest `@tag` or test title in the `.spec.ts` files.
- **Link Integrity**: Use granular links: `[test name](file:///path/to/test.spec.ts#L123-L145)`.

## 2. Coverage Stats Recalculation
If the plan includes a summary table (e.g., `Total Scenarios`, `UI Coverage %`):
- **Recount**: Manually (or via script) count the scenarios listed in the matrix vs the actual implemented tests.
- **Discrepancy Check**: Flag any requirements that have "Planned" scenarios but no "Implemented" links.

## 3. Anchor & ID Standards
- Use stable, searchable IDs for scenarios (e.g., `SCN-001`, `AUTH-MSS-01`).
- Ensure every requirement AC has at least one corresponding scenario ID in the matrix.

## 4. Documentation Sync Workflow
1. **Source of Truth**: The `coverage_plan/*.md` is the source of truth for *what* is tested.
2. **Implementation Proof**: the `docs/tests/**/*.md` (TDD/BDD) provides the *proof* with links to code.
3. **Synchronization**: Run a global search for each Scenario ID to ensure it exists in both the plan and the formal documentation.

## Checklist

- [ ] **Stats Updated**: Summary counts in the coverage plan match the list.
- [ ] **Links Verified**: All file/line links in the TDD docs are valid.
- [ ] **Requirements Covered**: No AC is left without a mapped scenario.
- [ ] **Consistency Check**: Scenario names are consistent across the plan, docs, and code.
