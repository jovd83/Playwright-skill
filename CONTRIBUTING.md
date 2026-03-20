# Contributing

## Goals

Contributions should make the pack easier to trust, easier to route, and easier to maintain. Favor improvements that sharpen a skill's operating contract, reduce ambiguity, or add deterministic validation.

## Repository Conventions

- Treat the root [`SKILL.md`](SKILL.md) as a routing layer, not as a giant encyclopedia.
- Keep deep guidance inside focused subskills or reference files.
- Prefer progressive disclosure: put selection logic in `SKILL.md`, then move detailed examples and recipes into nearby reference guides.
- Keep runtime execution concerns separate from project-local persistent artifacts and separate both from any shared-memory system.
- Do not add speculative frameworks, placeholders, or empty scaffolding.

## Editing Skills

When changing a skill:

1. Keep the YAML frontmatter limited to `name` and `description`.
2. Make the `description` trigger-oriented and specific about when the skill should be used.
3. Keep the body procedural and focused on what another agent needs in order to execute well.
4. Prefer concise instructions over repeated theory.
5. Add or update `agents/openai.yaml` for root or user-facing entrypoints when discoverability matters.
6. Update linked docs if routing or file locations change.

## Writing Good Skill Instructions

- State scope, responsibilities, and boundaries explicitly.
- Define inputs, outputs, and stop conditions for planning or documentation skills.
- Avoid rigid "always ask the user" flows when the agent can safely infer the next step.
- Use strong guardrails where the workflow is brittle.
- Use higher freedom where the task is contextual and multiple valid approaches exist.

## Validation

Run this before committing:

```bash
python scripts/validate_skill_repo.py
```

If you add, remove, rename, or move skills, refresh the inventory report too:

```bash
python scripts/generate_skill_inventory.py
```

If you touch handoff or session-state tooling, also run:

```bash
python documentation/shared/scripts/run_handoff_ci_checks.py --format text
```

## Pull Request Expectations

- Explain the user-facing or maintainer-facing problem being solved.
- Call out any behavior changes in routing, output contracts, validation, or repo structure.
- Update [`CHANGELOG.md`](CHANGELOG.md) for notable changes.
- Refresh [`reports/skill-inventory.md`](reports/skill-inventory.md) when the skill inventory changes.
- Keep diffs purposeful. A smaller, sharper improvement is better than broad churn without stronger guarantees.

## When Adding a New Skill

Add a new skill only when one of these is true:

- the workflow is distinct enough that a separate trigger improves routing,
- the guidance would otherwise overload an existing `SKILL.md`,
- a deterministic script or reference bundle materially reduces repeated effort.

Before adding a new skill, ask whether the change could instead be:

- a new reference guide under an existing skill,
- a refinement to routing in an existing entrypoint,
- a script or template in a current skill directory.

## Style

- Prefer ASCII unless the file already requires something else.
- Use concrete terminology instead of marketing language.
- Keep examples realistic and repo-relative where possible.
- Write for maintainers and agents who need to act, not for a slide deck.
