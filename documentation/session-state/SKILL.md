---
name: session-state
description: Use when Playwright work spans multiple sessions or operators and a live resume pointer is needed. Maintain a current state file that records the latest completed step, current in-progress step, remaining work, blockers, touched files, resume commands, validation snapshot, and links to the latest handover.
metadata:
  author: jovd83
  version: 2.0.0
  dispatcher-category: testing
  dispatcher-capabilities: session-state, playwright-session-state
  dispatcher-accepted-intents: record_playwright_session_state
  dispatcher-input-artifacts: work_state, touched_files, blockers
  dispatcher-output-artifacts: session_state_record, resume_pointer
  dispatcher-stack-tags: playwright, session-state, operations
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# Session State

Maintain a small, durable state file that always reflects the current truth of the task.

Read [references/template.md](references/template.md) when creating or refreshing the state file.
Read [references/troubleshooting.md](references/troubleshooting.md) when the current state is stale, contradictory, missing, or cannot safely drive resume work.
Read [references/conflict-resolution.md](references/conflict-resolution.md) when the session-state file and handover disagree.
Read [../shared/references/handoff-bundle-trust-policy.example.json](../shared/references/handoff-bundle-trust-policy.example.json) when you need a checked-in bundle trust policy template.
Read [../shared/references/handoff-bundle-redaction-policy.example.json](../shared/references/handoff-bundle-redaction-policy.example.json) when you need a checked-in bundle redaction policy template.
Read [../shared/references/handoff-bundle-ci-policy.example.json](../shared/references/handoff-bundle-ci-policy.example.json) when the repo should fail CI if required checked-in bundle policies are missing.
Prefer `python ../shared/scripts/resolve_latest_handoff_pair.py --format json` when you need to locate the active linked pair deterministically from the project root.
Prefer `python ../shared/scripts/begin_handoff_session.py --holder codex --purpose "<purpose>" --task "<task>" --format text` when you need to begin active work in one step by creating or refreshing the live pair, claiming the lease, and reporting the workspace.
Prefer `python ../shared/scripts/end_handoff_session.py --holder codex --status ready-for-review --format text` when you need to stop active editing, release the lease, and get a final transfer-readiness verdict in one command.
Prefer `python ../shared/scripts/report_handoff_workspace.py --format text` when you need one deterministic operator report covering the active task, next action, live lease, workspace health, and recent milestones.
Prefer `python ../shared/scripts/check_handoff_readiness.py --format text` when you need a final yes-or-no transfer gate that explains whether the workspace is actually safe to hand off right now.
Prefer `python ../shared/scripts/list_handoff_history.py --format text` when you need a chronological view of the active pair and archived milestones.
Prefer `python ../shared/scripts/audit_handoff_workspace.py --format text` when you need to scan the full documentation root for invalid files, broken archived pairs, or partial history before trusting the live resume state.
Prefer `python ../shared/scripts/manage_handoff_lease.py claim --holder codex --purpose "<purpose>" --format text` when you are about to do multi-step edits on the live pair and need an explicit ownership claim that a human and another agent can both see.
Prefer `python ../shared/scripts/repair_handoff_workspace.py --updated-by codex --format text` when the workspace audit reports document-only drift that can be repaired deterministically across the live pair and archived snapshot cross-links.
Prefer `python ../shared/scripts/generate_handoff_pair.py --task "<task>" --status in-progress --updated-by codex --next-owner qa-reviewer` when you need to create or refresh both session-state and handover together with one timestamp.
Prefer `python ../shared/scripts/archive_handoff_pair.py --timestamp YYYYMMDD_HHmm` when you need a preserved snapshot of the current linked pair before further edits overwrite the live state.
Prefer `python ../shared/scripts/restore_handoff_pair.py --timestamp YYYYMMDD_HHmm --updated-by codex --force` when you need to reactivate an archived milestone back into the live `CURRENT.md` workflow.
Prefer `python ../shared/scripts/export_handoff_bundle.py --output <handoff-bundle.json> --format text` when you need to move the live resume state, lease context, and operator snapshot to another repo or machine as one artifact; it auto-loads `<test_documentation_root>/handoff-bundle-redaction-policy.json` when present.
Prefer `python ../shared/scripts/generate_handoff_bundle_redaction_policy.py --deny-redaction-path <bundle.path> --format text` when you need to scaffold the checked-in redaction policy at `<test_documentation_root>/handoff-bundle-redaction-policy.json`.
Prefer `python ../shared/scripts/validate_handoff_bundle_redaction_policy.py --format text` when you need to validate the checked-in redaction policy before relying on it.
Prefer `python ../shared/scripts/generate_handoff_bundle_trust_policy.py --require-signature --allowed-signature-scheme <scheme> --allowed-signer <actor> --allowed-key-id <key-id> --profile-name <env-or-role> --profile-template <env-or-role>=<dev|staging|prod> --profile-allowed-signer <env-or-role>=<actor> --profile-max-age-hours <env-or-role>=<hours> --profile-signature-secret-env <env-or-role>=<ENV_VAR> --default-profile <env-or-role> --format text` when you need to scaffold the checked-in repo policy at `<test_documentation_root>/handoff-bundle-trust-policy.json`.
Prefer `python ../shared/scripts/validate_handoff_bundle_trust_policy.py --profile <env-or-role> --format text` when you need to validate the checked-in repo policy or one of its named profiles before relying on it.
Prefer `python ../shared/scripts/generate_handoff_bundle_ci_policy.py --require-portable-bundle-policies --format text` when you need to scaffold the checked-in CI policy at `<test_documentation_root>/handoff-bundle-ci-policy.json`.
Prefer `python ../shared/scripts/validate_handoff_bundle_ci_policy.py --format text` when you need to validate the checked-in CI policy before relying on CI enforcement.
Prefer `python ../shared/scripts/run_handoff_ci_checks.py --format text` when you need one deterministic CI/local verification entrypoint for compile checks, checked-in trust policy validation, and the shared smoke suite.
Prefer `python ../shared/scripts/sign_handoff_bundle.py --bundle <handoff-bundle.json> --signer <actor> --key-id <key-id> --scheme sshsig --private-key-file <id_ed25519> --format text` when the portable bundle must carry an asymmetric authenticity proof in addition to integrity metadata; omit `--scheme sshsig` to keep the existing shared-secret HMAC flow.
Prefer `python ../shared/scripts/inspect_handoff_bundle.py --bundle <handoff-bundle.json> --format text` when you need to review or validate a portable handoff bundle before trusting or importing it.
Prefer `python ../shared/scripts/verify_handoff_bundle_signature.py --bundle <handoff-bundle.json> --required-scheme <scheme> --required-public-key-fingerprint <SHA256:...> --format text` when you need to verify the signer, scheme, key id, or SSH public key fingerprint on a signed bundle before trust or import.
Prefer `python ../shared/scripts/check_handoff_bundle_trust.py --bundle <handoff-bundle.json> --policy-profile <env-or-role> --format text` when you need a conservative yes-or-no trust verdict before importing a portable bundle; it auto-loads `<test_documentation_root>/handoff-bundle-trust-policy.json` when present.
Prefer `python ../shared/scripts/import_handoff_bundle.py --bundle <handoff-bundle.json> --policy-profile <env-or-role> --format text` when you need to restore an exported bundle into the target workspace and rewrite the local pointers deterministically; `--trusted-only` auto-loads `<test_documentation_root>/handoff-bundle-trust-policy.json` when present.
Prefer `python ../shared/scripts/update_handoff_pair.py --session-state <CURRENT.md> --updated-by codex` when the linked pair already exists and you need to refresh shared state in place without rewriting the richer handover sections.
Prefer `python ../shared/scripts/summarize_handoff_pair.py --session-state <CURRENT.md> --format text` when you need a fast resume brief, or `--format json` for machine-readable state.
Prefer `python ../shared/scripts/reconcile_handoff_pair.py --handover <handover.md> --session-state <CURRENT.md> --updated-by codex` to reconcile a divergent pair before handoff.
Prefer `python ../shared/scripts/validate_handoff_pair.py --handover <handover.md> --session-state <CURRENT.md>` to validate the linked pair in one command when both files exist.
Prefer `python scripts/generate_session_state.py --task "<task>" --status in-progress --updated-by codex --next-owner qa-reviewer` to scaffold `CURRENT.md` deterministically.
Run `python scripts/validate_session_state.py <path-to-current.md>` before handing work to another operator.


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

## 1. Resolve the documentation root

1. Run `python ../shared/scripts/resolve_test_docs_root.py --ensure session-state` when you need to discover the root explicitly.
2. Use the resolved project-defined test documentation root when one already exists.
3. Use `docs/tests/` when the project does not define another root.
4. Create `<test_documentation_root>/session-state/` if it does not exist.
5. Create `<test_documentation_root>/handovers/` as well when the session-state file will point to a handover.

## 2. Choose the target session-state file

1. Keep the live resume pointer at `<test_documentation_root>/session-state/CURRENT.md`.
2. Overwrite `CURRENT.md` with the newest truth instead of appending stale history.
3. Create an archived milestone snapshot such as `YYYYMMDD_HHmm_session-state.md` only when the history is worth preserving.

## 3. Generate the session-state file deterministically

1. Prefer `python ../shared/scripts/generate_handoff_pair.py ...` when you need to create both files together with one timestamp.
2. Prefer `python ../shared/scripts/begin_handoff_session.py --holder <actor> --purpose "<purpose>" --task "<task>" --format text` when you need to start or resume active work and want the live pair plus lease aligned in one command.
3. Omit `--root` unless you need to override discovery; the generator resolves the documentation root automatically.
4. Run `python ../shared/scripts/list_handoff_history.py --format text` when you need to review the active pair and archived milestones before choosing whether to refresh `CURRENT.md` or create a snapshot.
5. Prefer `python ../shared/scripts/archive_handoff_pair.py --timestamp YYYYMMDD_HHmm` before major edits when you need a preserved snapshot of the current linked pair.
6. Prefer `python ../shared/scripts/restore_handoff_pair.py --timestamp YYYYMMDD_HHmm --updated-by <actor> --force` when you need to reactivate a prior archived milestone as the live pair.
7. Prefer `python ../shared/scripts/export_handoff_bundle.py --output <handoff-bundle.json> --format text` when the live resume state must leave the current repo or machine without losing the linked pair, lease context, operator snapshot, and current git state; obvious secrets are redacted by default, checked-in or explicit redaction policies can add allow/deny path rules, and the bundle captures a git patch summary fingerprint.
8. Prefer `python ../shared/scripts/generate_handoff_bundle_trust_policy.py --require-signature --allowed-signature-scheme <scheme> --allowed-signer <actor> --allowed-key-id <key-id> --allowed-public-key-fingerprint <SHA256:...> --profile-name <env-or-role> --profile-template <env-or-role>=<dev|staging|prod> --default-profile <env-or-role> --revoked-key-id <old-key-id> --format text` when you need to scaffold the repo policy file, including signer rotation, allowed schemes, SSH key fingerprints, named environment or role profiles, preset environment templates, or revoked key ids.
9. Prefer `python ../shared/scripts/validate_handoff_bundle_trust_policy.py --profile <env-or-role> --format text` before enforcing a checked-in repo policy.
10. Prefer `python ../shared/scripts/inspect_handoff_bundle.py --bundle <handoff-bundle.json> --format text` before import when you need to verify the embedded pair, lease payload, captured source readiness, git metadata, patch-summary fingerprints, signature scheme and key fingerprint, and the applied redaction policy deterministically.
11. Prefer `python ../shared/scripts/sign_handoff_bundle.py --bundle <handoff-bundle.json> --signer <actor> --key-id <key-id> --scheme sshsig --private-key-file <id_ed25519> --format text` when the bundle must be portable across repos or machines with an asymmetric authenticity proof; use the default HMAC mode when a shared secret is acceptable.
12. Prefer `python ../shared/scripts/verify_handoff_bundle_signature.py --bundle <handoff-bundle.json> --required-scheme <scheme> --required-public-key-fingerprint <SHA256:...> --format text` before trust or import when you need to confirm the signer cryptographically.
13. Prefer `python ../shared/scripts/check_handoff_bundle_trust.py --bundle <handoff-bundle.json> --policy-profile <env-or-role> --secret-file <path> --format text` before import when you want the repo policy in `<test_documentation_root>/handoff-bundle-trust-policy.json` applied automatically.
14. Prefer `python ../shared/scripts/import_handoff_bundle.py --bundle <handoff-bundle.json> --policy-profile <env-or-role> --trusted-only --secret-file <path> --dry-run --format text` when you need a no-write preview of the exact files and lease data the import would touch.
15. Pass `--policy-file <path>` when you need to override the default policy location or evaluate the bundle against a different checked-in policy.
16. Prefer `python ../shared/scripts/generate_handoff_bundle_redaction_policy.py --deny-redaction-path <bundle.path> --format text` when you need to scaffold the checked-in redaction policy.
17. Prefer `python ../shared/scripts/validate_handoff_bundle_redaction_policy.py --format text` before enforcing a checked-in redaction policy.
18. Prefer `python ../shared/scripts/generate_handoff_bundle_ci_policy.py --require-trust-policy --require-redaction-policy --format text` when the repo needs a checked-in CI policy that declares which bundle policy files are mandatory.
19. Prefer `python ../shared/scripts/validate_handoff_bundle_ci_policy.py --format text` before relying on a checked-in CI policy.
20. Prefer `python ../shared/scripts/run_handoff_ci_checks.py --format text` before shipping workflow changes when you need the same compile, trust-policy, redaction-policy, CI-policy, and smoke checks CI will execute.
21. Prefer `python ../shared/scripts/update_handoff_pair.py --session-state <CURRENT.md> --updated-by <actor>` when both linked files already exist and you need to refresh status, ownership, current step, remaining work, blockers, or resume commands in place.
22. Run `python scripts/generate_session_state.py --task "<task>" --status <status> --updated-by <actor> --next-owner <actor-or-None>` when you need only the session-state file.
23. Add `--last-completed-step`, `--current-step`, `--remaining-step`, `--blocker`, `--file-touched`, and `--command-to-resume` as needed.
24. Pass `--handover-pointer` when a handover already exists.
25. Use `--output` only when you intentionally want a snapshot file instead of `CURRENT.md`.

## 4. Populate every required section

1. `Task`: state the task goal in one sentence.
2. `Status`: use one of `not-started`, `in-progress`, `blocked`, `ready-for-review`, `done`.
3. `Last updated`: record the most recent update timestamp in ISO 8601 format with timezone.
4. `Updated by`: record the human or AI identifier that last updated the file.
5. `Next owner`: record who should act next; use `None` only when status is `done`.
6. `Last completed step`: record the last fully completed action.
7. `Current step`: record the exact action currently in progress.
8. `Remaining steps`: list the remaining actions in execution order.
9. `Blockers`: record active blockers and what is needed to unblock them.
10. `Decisions and assumptions`: record the decisions already made and the assumptions currently shaping the work.
11. `Files touched`: list the files that the next operator should inspect first.
12. `Commands to resume`: list the first commands that should be run to continue the task.
13. `Validation snapshot`: record the latest checks that passed, failed, or were skipped.
14. `Artifacts`: list relevant logs, traces, screenshots, reports, or generated files.
15. `Handover pointer`: link to the latest handover when one exists, using a forward-slash relative path such as `../handovers/20260312_1530_handover.md`.

## 5. Apply the canonical status model

1. Use the same status vocabulary in the session-state file and the handover document.
2. Use `not-started` when the task exists but execution has not begun.
3. Use `in-progress` when work is actively moving and the next operator can continue immediately.
4. Use `blocked` when progress is stopped by a dependency, unanswered decision, failing prerequisite, or missing access.
5. Use `ready-for-review` when implementation work is complete enough for review but not yet fully closed.
6. Use `done` only when no more execution or review work is expected.
7. Do not use synonyms such as `completed`, `paused`, `partial`, `pending-review`, or `finished`.
8. Use only these transitions unless the user explicitly defines a different workflow: `not-started -> in-progress`, `not-started -> blocked`, `in-progress -> blocked`, `blocked -> in-progress`, `in-progress -> ready-for-review`, `ready-for-review -> in-progress`, `ready-for-review -> done`.
9. Treat `done` as terminal.

## 6. Refresh the file whenever the task state changes

1. Create `CURRENT.md` at the start of substantial work if no current state exists.
2. Update `CURRENT.md` after each meaningful milestone.
3. Update `CURRENT.md` before ending the session.
4. Update `CURRENT.md` whenever blockers, assumptions, ownership, or resume commands change.

## 7. Write the file so another operator can resume immediately

1. Keep the file short and current.
2. Prefer exact paths, commands, identifiers, and artifact locations.
3. Use ISO 8601 timestamps with timezone for `Last updated`.
4. Use stable human or agent identifiers for `Updated by` and `Next owner`.
5. Replace outdated statements instead of leaving contradictory history behind.
6. Make the next action obvious without requiring repo re-discovery.
7. Claim the live lease before multi-step edits and release it when the next operator should take over.

## 8. Resolve conflicts with the handover

1. Compare `Last updated`, linked pointers, repo state, and validation artifacts before trusting either document.
2. Prefer concrete evidence such as the working tree, generated artifacts, logs, traces, and test results over both documents.
3. Prefer `python ../shared/scripts/reconcile_handoff_pair.py --handover <handover.md> --session-state <CURRENT.md> --updated-by <actor>` when the divergence is document-only and can be reconciled deterministically.
4. When no concrete evidence contradicts it, treat `CURRENT.md` as authoritative for active execution fields: `Status` while work is still active, `Current step`, `Remaining steps`, `Next owner`, `Files touched`, and `Commands to resume`.
5. When no concrete evidence contradicts it, treat the handover as authoritative for transfer-summary fields: `Task summary`, `What was done`, `Validation status`, `Patterns used`, `Anti-patterns used`, `Strengths of the changes`, `Weaknesses of the changes`, `How things could be improved`, and `Files added or modified`.
6. If one file says `done` but the other still shows remaining work, active blockers, or a non-`None` next owner, do not keep `done`; downgrade both files to `ready-for-review` or `in-progress`, whichever matches the real state.
7. After reconciling the conflict, update both files so they match on `Status`, `Last updated`, `Updated by`, `Next owner`, and cross-links.

## 9. Validate and coordinate with the handover

1. Run `python scripts/validate_session_state.py <path-to-current.md>`.
2. Run `python ../shared/scripts/validate_handoff_pair.py --handover <handover.md> --session-state <CURRENT.md>` when both files exist, or omit both path flags from the project root to validate the latest resolved pair.
3. Run `python ../shared/scripts/report_handoff_workspace.py --format text` when you need the fastest combined view of resume state, lease ownership, workspace health, and recent history.
4. Run `python ../shared/scripts/end_handoff_session.py --holder <actor> --status <status> --format text` when you want one deterministic end-of-session command that updates the live pair, releases the lease, and returns the readiness verdict.
5. Run `python ../shared/scripts/check_handoff_readiness.py --format text` when you need the final transfer verdict and the exact blocking reasons if the workspace is not yet safe to hand off.
6. Run `python ../shared/scripts/summarize_handoff_pair.py --session-state <CURRENT.md> --format text` when you need a compact transfer brief for the next operator, or omit both path flags from the project root to summarize the latest resolved pair.
7. Run `python ../shared/scripts/audit_handoff_workspace.py --format text` when you need to verify that archived milestones and orphan snapshots are not hiding broken history outside the active pair.
8. Run `python ../shared/scripts/repair_handoff_workspace.py --updated-by <actor> --format text` when the audit reports document-only drift that should be repaired before handoff.
9. Run `python ../shared/scripts/export_handoff_bundle.py --output <handoff-bundle.json> --format text` when the work must continue in another repo clone, workspace, or machine.
10. Run `python ../shared/scripts/generate_handoff_bundle_trust_policy.py --require-signature --allowed-signature-scheme <scheme> --allowed-signer <actor> --allowed-key-id <new-key-id> --allowed-public-key-fingerprint <SHA256:...> --profile-name <env-or-role> --profile-template <env-or-role>=<dev|staging|prod> --default-profile <env-or-role> --revoked-key-id <old-key-id> --format text` when the target repo needs a checked-in policy with explicit rotation, scheme, SSH key fingerprint, named profiles, preset environment templates, or revocation rules.
11. Run `python ../shared/scripts/validate_handoff_bundle_trust_policy.py --profile <env-or-role> --format text` before relying on the checked-in policy.
12. Run `python ../shared/scripts/sign_handoff_bundle.py --bundle <handoff-bundle.json> --signer <actor> --key-id <key-id> --scheme sshsig --private-key-file <id_ed25519> --format text` when the transfer artifact must prove who authorized it without sharing a secret; omit `--scheme sshsig` for the existing HMAC flow.
13. Run `python ../shared/scripts/verify_handoff_bundle_signature.py --bundle <handoff-bundle.json> --required-scheme <scheme> --required-public-key-fingerprint <SHA256:...> --format text` before import when you need a deterministic authenticity check on the transferred artifact.
14. Run `python ../shared/scripts/check_handoff_bundle_trust.py --bundle <handoff-bundle.json> --policy-profile <env-or-role> --secret-file <path> --format text` when you need the checked-in repo policy applied automatically before allowing import.
15. Run `python ../shared/scripts/import_handoff_bundle.py --bundle <handoff-bundle.json> --policy-profile <env-or-role> --trusted-only --secret-file <path> --dry-run --format text` first when you want to preview the exact import without touching files.
16. Run `python ../shared/scripts/generate_handoff_bundle_redaction_policy.py --deny-redaction-path <bundle.path> --format text` when the target repo needs a checked-in redaction policy for export control.
17. Run `python ../shared/scripts/validate_handoff_bundle_redaction_policy.py --format text` before relying on the checked-in redaction policy.
18. Run `python ../shared/scripts/generate_handoff_bundle_ci_policy.py --require-trust-policy --require-redaction-policy --format text` when the target repo needs a checked-in CI policy that declares which bundle policy files must exist.
19. Run `python ../shared/scripts/validate_handoff_bundle_ci_policy.py --format text` before relying on the checked-in CI policy.
20. Run `python ../shared/scripts/run_handoff_ci_checks.py --format text` when you need the same compile, trust-policy, redaction-policy, CI-policy, and smoke checks CI will enforce.
21. Store the checked-in repo policy at `<test_documentation_root>/handoff-bundle-trust-policy.json` when bundle imports must follow fixed signer, age, lease, ownership, or profile-based environment rules.
22. Store the checked-in redaction policy at `<test_documentation_root>/handoff-bundle-redaction-policy.json` when exported bundles must follow fixed path, keyword, or regex redaction rules.
23. Store the checked-in CI policy at `<test_documentation_root>/handoff-bundle-ci-policy.json` when CI should fail if required bundle policy files are missing.
24. Run `python ../shared/scripts/manage_handoff_lease.py release --holder <actor> --format text` when you need to release the lease without the end-of-session wrapper.
25. Fix every validation error before handing work to another operator.
26. Treat `CURRENT.md` as the live resume pointer.
27. Treat the handover document as the broader transfer summary.
28. When pausing incomplete work, update both files together.
29. Keep the handover status and session-state status identical.
30. Keep `Handover pointer` in forward-slash form instead of Windows-style backslashes.

## 10. Troubleshoot when the session-state file is unsafe to use

1. Open [references/troubleshooting.md](references/troubleshooting.md) when `CURRENT.md` is missing, the handover pointer is stale, statuses do not match, required sections are empty, the workspace audit reports partial history, the workspace repair command cannot resolve the drift safely, the live lease is stale or conflicting, or validation details cannot be trusted.
