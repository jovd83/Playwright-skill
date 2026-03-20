---
name: playwright-ci
description: CI and delivery skill for Playwright automation. Use when Codex needs to design, debug, or optimize Playwright execution in GitHub Actions, GitLab CI, CircleCI, Azure DevOps, Jenkins, Docker, sharded pipelines, artifact workflows, or shared setup and teardown.
---

# Playwright CI

Use this skill when the main problem is pipeline execution rather than test authoring.

## CI Standards

1. Prefer deterministic setup over clever pipeline shortcuts.
2. Capture traces, screenshots, and reports where they help triage failures quickly.
3. Scale horizontally with sharding before over-sizing single runners.
4. Cache browser binaries and other stable dependencies deliberately.
5. Keep CI retries informative, not silent flake camouflage.

## Read by Need

| Need | Guide |
|---|---|
| GitHub Actions | [ci-github-actions.md](ci-github-actions.md) |
| GitLab CI | [ci-gitlab.md](ci-gitlab.md) |
| Other providers | [ci-other.md](ci-other.md) |
| Sharding and scaling | [parallel-and-sharding.md](parallel-and-sharding.md), [projects-and-dependencies.md](projects-and-dependencies.md) |
| Containers | [docker-and-containers.md](docker-and-containers.md) |
| Reports and artifacts | [reporting-and-artifacts.md](reporting-and-artifacts.md) |
| Coverage and setup orchestration | [test-coverage.md](test-coverage.md), [global-setup-teardown.md](global-setup-teardown.md) |

## Output Bias

When solving CI tasks, prefer:

- concrete workflow or pipeline changes,
- exact commands and cache locations,
- artifact and failure-diagnostics recommendations,
- explicit tradeoffs when the pipeline needs faster feedback versus deeper debugging.
