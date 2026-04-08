---
name: handover
description: Use when Playwright work must be handed from one operator to another, including at task completion, during mid-task pauses, after a blocker, or before review. Create a structured handover that records what was completed, where execution stopped, what remains, validation status, blockers, and the exact steps to resume safely.
metadata:
  author: jovd83
  version: "2.0.0"
  dispatcher-category: testing
  dispatcher-capabilities: handover, playwright-handover
  dispatcher-accepted-intents: create_playwright_handover
  dispatcher-input-artifacts: work_summary, validation_status, blockers
  dispatcher-output-artifacts: handover_document, resume_steps
  dispatcher-stack-tags: playwright, handover, operations
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# Handover

Create a handover document whenever work needs to be transferred from one operator to another.

Read [references/template.md](references/template.md) when generating the final document.
Read [references/troubleshooting.md](references/troubleshooting.md) when the handover is inconsistent, incomplete, or cannot be used to resume work safely.
Read [references/conflict-resolution.md](references/conflict-resolution.md) when the handover and session-state file disagree.
Read [../shared/references/handoff-bundle-trust-policy.example.json](../shared/references/handoff-bundle-trust-policy.example.json) when you need a checked-in bundle trust policy template.
Read [../shared/references/handoff-bundle-redaction-policy.example.json](../shared/references/handoff-bundle-redaction-policy.example.json) when you need a checked-in bundle redaction policy template.
Read [../shared/references/handoff-bundle-ci-policy.example.json](../shared/references/handoff-bundle-ci-policy.example.json) when the repo should fail CI if required checked-in bundle policies are missing.
Prefer `python ../shared/scripts/resolve_latest_handoff_pair.py --format json` when you need to locate the active linked pair deterministically from the project root.
Prefer `python ../shared/scripts/begin_handoff_session.py --holder codex --purpose "<purpose>" --task "<task>" --format text` when you need to begin active work in one step by creating or refreshing the live pair, claiming the lease, and reporting the workspace.
Prefer `python ../shared/scripts/end_handoff_session.py --holder codex --status ready-for-review --format text` when you need to stop active editing, release the lease, and get a final transfer-readiness verdict in one command.
Prefer `python ../shared/scripts/report_handoff_workspace.py --format text` when you need one deterministic operator report covering the active task, next action, live lease, workspace health, and recent milestones.
Prefer `python ../shared/scripts/check_handoff_readiness.py --format text` when you need a final yes-or-no transfer gate that explains whether the workspace is actually safe to hand off right now.
Prefer `python ../shared/scripts/list_handoff_history.py --format text` when you need a chronological view of the active pair and archived milestones.
Prefer `python ../shared/scripts/audit_handoff_workspace.py --format text` when you need to scan the full documentation root for invalid files, broken archived pairs, or partial history before trusting the handoff workspace.
Prefer `python ../shared/scripts/manage_handoff_lease.py claim --holder codex --purpose "<purpose>" --format text` when you are about to do multi-step edits on the live pair and need an explicit ownership claim that a human and another agent can both see.
Prefer `python ../shared/scripts/repair_handoff_workspace.py --updated-by codex --format text` when the workspace audit reports document-only drift that can be repaired deterministically across the live pair and archived snapshot cross-links.
Prefer `python ../shared/scripts/generate_handoff_pair.py --task "<task>" --status in-progress --updated-by codex --next-owner qa-reviewer` when you need to create or refresh both handover and session-state together with one timestamp.
Prefer `python ../shared/scripts/archive_handoff_pair.py --timestamp YYYYMMDD_HHmm` when you need a preserved snapshot of the current linked pair before further edits overwrite the live state.
Prefer `python ../shared/scripts/restore_handoff_pair.py --timestamp YYYYMMDD_HHmm --updated-by codex --force` when you need to reactivate an archived milestone back into the live `CURRENT.md` workflow.
Prefer `python ../shared/scripts/export_handoff_bundle.py --output <handoff-bundle.json> --format text` when you need to move the current linked pair, lease context, and operator snapshot to another repo or machine as one artifact; it auto-loads `<test_documentation_root>/handoff-bundle-redaction-policy.json` when present.
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
Prefer `python ../shared/scripts/update_handoff_pair.py --handover <handover.md> --updated-by codex` when the linked pair already exists and you need to refresh shared state in place without rewriting the richer handover sections.
Prefer `python ../shared/scripts/summarize_handoff_pair.py --handover <handover.md> --format text` when you need a fast resume brief, or `--format json` for machine-readable state.
Prefer `python ../shared/scripts/reconcile_handoff_pair.py --handover <handover.md> --session-state <CURRENT.md> --updated-by codex` to reconcile a divergent pair before transfer.
Prefer `python ../shared/scripts/validate_handoff_pair.py --handover <handover.md> --session-state <CURRENT.md>` to validate the linked pair in one command when both files exist.
Prefer `python scripts/generate_handover.py --task-summary "<summary>" --status in-progress --updated-by codex --next-owner qa-reviewer` to scaffold new handover files deterministically.
Run `python scripts/validate_handover.py <path-to-handover.md>` before transferring work.

## 1. Resolve the documentation root

1. Run `python ../shared/scripts/resolve_test_docs_root.py --ensure handover` when you need to discover the root explicitly.
2. Use the resolved project-defined test documentation root when one already exists.
3. Use `docs/tests/` when the project does not define another root.
4. Create `<test_documentation_root>/handovers/` if it does not exist.
5. Create `<test_documentation_root>/session-state/` as well when the handover status will not be `done`.

## 2. Choose the target handover file

1. Create a new handover file for each pause, completion, or operator transfer.
2. Store the file in `<test_documentation_root>/handovers/`.
3. Name the file `YYYYMMDD_HHmm_handover.md`.
4. Use local project time for the timestamp.

## 3. Generate the handover deterministically

1. Prefer `python ../shared/scripts/generate_handoff_pair.py ...` when you need to create both files together with one timestamp.
2. Prefer `python ../shared/scripts/begin_handoff_session.py --holder <actor> --purpose "<purpose>" --task "<task>" --format text` when you need to start or resume active work and want the live pair plus lease aligned in one command.
3. Omit `--root` unless you need to override discovery; the generator resolves the documentation root automatically.
4. Run `python ../shared/scripts/list_handoff_history.py --format text` when you need to review the active pair and archived milestones before choosing the next handover file to update or supersede.
5. Prefer `python ../shared/scripts/archive_handoff_pair.py --timestamp YYYYMMDD_HHmm` before major edits when you need a preserved snapshot of the current linked pair.
6. Prefer `python ../shared/scripts/restore_handoff_pair.py --timestamp YYYYMMDD_HHmm --updated-by <actor> --force` when you need to reactivate a prior archived milestone as the live pair.
7. Prefer `python ../shared/scripts/export_handoff_bundle.py --output <handoff-bundle.json> --format text` when the handoff must leave the current repo or machine without losing the live pair, lease context, operator snapshot, and current git state; obvious secrets are redacted by default, checked-in or explicit redaction policies can add allow/deny path rules, and the bundle captures a git patch summary fingerprint.
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
21. Prefer `python ../shared/scripts/update_handoff_pair.py --handover <handover.md> --updated-by <actor>` when both linked files already exist and you need to refresh status, ownership, current step, remaining work, blockers, or resume commands in place.
22. Run `python scripts/generate_handover.py --task-summary "<summary>" --status <status> --updated-by <actor> --next-owner <actor-or-None>` when you need only the handover file.
23. Add `--what-was-done`, `--remaining-work`, `--last-completed-step`, `--current-step`, `--first-file`, and `--next-command` as needed.
24. Pass `--session-state-pointer` when the default pointer is not correct.
25. Use `--output` when you need an explicit filename.

## 4. Populate every required section

1. `Task summary`: state the task goal in one or two sentences.
2. `Status`: use one of `not-started`, `in-progress`, `blocked`, `ready-for-review`, `done`.
3. `Last updated`: record the most recent update timestamp in ISO 8601 format with timezone.
4. `Updated by`: record the human or AI identifier that last updated the document.
5. `Next owner`: record who should act next; use `None` only when status is `done`.
6. `What was done`: summarize the concrete actions already taken.
7. `Last completed step`: record the last fully completed action.
8. `Current step`: describe the in-progress action, or say `None` if no partial step is in flight.
9. `Remaining work`: list the next actions in execution order.
10. `Blockers and decisions`: record blockers, assumptions, and decisions already made.
11. `Validation status`: state what passed, failed, or was not run.
12. `Resume instructions`: provide the first file to open, the next command to run, and any prerequisites.
13. `Skills and subskills used`: record the skills used and why they were used.
14. `Non-skill actions and suggestions`: record actions not covered by an existing skill and suggest follow-up skill work when appropriate.
15. `Patterns used`: record the implementation or documentation patterns used and why.
16. `Anti-patterns used`: record unavoidable anti-patterns and why they were necessary.
17. `Strengths of the changes`: summarize the main benefits of the completed work.
18. `Weaknesses of the changes`: summarize the main risks or follow-up concerns.
19. `How things could be improved`: list concrete improvement ideas for the next iteration.
20. `Files added or modified`: group files under `Documentation`, `POMs`, `Test Scripts`, `Configurations`, and `Other`, then explain why they matter.
21. `Session-state pointer`: link the live session-state file when the task is not `done`, using a forward-slash relative path such as `../session-state/CURRENT.md`.

## 5. Apply the canonical status model

1. Use the same status vocabulary in the handover and the session-state file.
2. Use `not-started` when the task exists but work has not begun.
3. Use `in-progress` when work is underway and can continue.
4. Use `blocked` when progress cannot continue until an external dependency, decision, or fix is resolved.
5. Use `ready-for-review` when implementation work is complete enough for review but not yet fully closed.
6. Use `done` only when the task is complete and no further action is expected.
7. Do not use synonyms such as `completed`, `paused`, `partial`, `pending-review`, or `finished`.
8. Use only these transitions unless the user explicitly defines a different workflow: `not-started -> in-progress`, `not-started -> blocked`, `in-progress -> blocked`, `blocked -> in-progress`, `in-progress -> ready-for-review`, `ready-for-review -> in-progress`, `ready-for-review -> done`.
9. Treat `done` as terminal.

## 6. Write the handover so another operator can execute immediately

1. Prefer exact paths, commands, branch names, test commands, and artifact locations over general statements.
2. Use ISO 8601 timestamps with timezone for `Last updated`.
3. Use stable human or agent identifiers for `Updated by` and `Next owner`.
4. State unresolved issues explicitly instead of implying them.
5. Remove stale TODO items when they are no longer relevant.
6. Keep the document concise, but make the next step executable without re-discovery.
7. Claim the live lease before multi-step edits and release it when the handoff is ready to transfer.

## 7. Resolve conflicts with the session-state file

1. Compare `Last updated`, linked pointers, repo state, and validation artifacts before trusting either document.
2. Prefer concrete evidence such as the working tree, generated artifacts, logs, traces, and test results over both documents.
3. Prefer `python ../shared/scripts/reconcile_handoff_pair.py --handover <handover.md> --session-state <CURRENT.md> --updated-by <actor>` when the divergence is document-only and can be reconciled deterministically.
4. When no concrete evidence contradicts it, treat `CURRENT.md` as authoritative for active execution fields: `Status` while work is still active, `Current step`, `Remaining work`, `Next owner`, and the immediate resume path.
5. When no concrete evidence contradicts it, treat the handover as authoritative for transfer-summary fields: `What was done`, `Validation status`, `Patterns used`, `Anti-patterns used`, `Strengths of the changes`, `Weaknesses of the changes`, `How things could be improved`, and `Files added or modified`.
6. If one file says `done` but the other still shows remaining work, active blockers, or a non-`None` next owner, do not keep `done`; downgrade both files to `ready-for-review` or `in-progress`, whichever matches the real state.
7. After reconciling the conflict, update both files so they match on `Status`, `Last updated`, `Updated by`, `Next owner`, and cross-links.

## 8. Validate and transfer

1. Run `python scripts/validate_handover.py <path-to-handover.md>`.
2. Fix every validation error before transferring work.
3. Run `python ../shared/scripts/validate_handoff_pair.py --handover <handover.md> --session-state <CURRENT.md>` when both files exist, or omit both path flags from the project root to validate the latest resolved pair.
4. Run `python ../shared/scripts/report_handoff_workspace.py --format text` when you need the fastest combined view of resume state, lease ownership, workspace health, and recent history.
5. Run `python ../shared/scripts/end_handoff_session.py --holder <actor> --status <status> --format text` when you want one deterministic end-of-session command that updates the live pair, releases the lease, and returns the readiness verdict.
6. Run `python ../shared/scripts/check_handoff_readiness.py --format text` when you need the final transfer verdict and the exact blocking reasons if the workspace is not yet safe to hand off.
7. Run `python ../shared/scripts/summarize_handoff_pair.py --handover <handover.md> --format text` when you need a compact transfer brief for the next operator, or omit both path flags from the project root to summarize the latest resolved pair.
8. Run `python ../shared/scripts/audit_handoff_workspace.py --format text` when you need to verify that archived milestones and orphan snapshots are not hiding broken history outside the active pair.
9. Run `python ../shared/scripts/repair_handoff_workspace.py --updated-by <actor> --format text` when the audit reports document-only drift that should be repaired before transfer.
10. Run `python ../shared/scripts/export_handoff_bundle.py --output <handoff-bundle.json> --format text` when the transfer must continue in another repo clone, workspace, or machine.
11. Run `python ../shared/scripts/generate_handoff_bundle_trust_policy.py --require-signature --allowed-signature-scheme <scheme> --allowed-signer <actor> --allowed-key-id <new-key-id> --allowed-public-key-fingerprint <SHA256:...> --profile-name <env-or-role> --profile-template <env-or-role>=<dev|staging|prod> --default-profile <env-or-role> --revoked-key-id <old-key-id> --format text` when the target repo needs a checked-in policy with explicit rotation, scheme, SSH key fingerprint, named profiles, preset environment templates, or revocation rules.
12. Run `python ../shared/scripts/validate_handoff_bundle_trust_policy.py --profile <env-or-role> --format text` before relying on the checked-in policy.
13. Run `python ../shared/scripts/sign_handoff_bundle.py --bundle <handoff-bundle.json> --signer <actor> --key-id <key-id> --scheme sshsig --private-key-file <id_ed25519> --format text` when the transfer artifact must prove who authorized it without sharing a secret; omit `--scheme sshsig` for the existing HMAC flow.
14. Run `python ../shared/scripts/verify_handoff_bundle_signature.py --bundle <handoff-bundle.json> --required-scheme <scheme> --required-public-key-fingerprint <SHA256:...> --format text` before import when you need a deterministic authenticity check on the transferred artifact.
15. Run `python ../shared/scripts/check_handoff_bundle_trust.py --bundle <handoff-bundle.json> --policy-profile <env-or-role> --secret-file <path> --format text` when you need the checked-in repo policy applied automatically before allowing import.
16. Run `python ../shared/scripts/import_handoff_bundle.py --bundle <handoff-bundle.json> --policy-profile <env-or-role> --trusted-only --secret-file <path> --dry-run --format text` first when you want to preview the exact import without touching files.
17. Run `python ../shared/scripts/generate_handoff_bundle_redaction_policy.py --deny-redaction-path <bundle.path> --format text` when the target repo needs a checked-in redaction policy for export control.
18. Run `python ../shared/scripts/validate_handoff_bundle_redaction_policy.py --format text` before relying on the checked-in redaction policy.
19. Run `python ../shared/scripts/generate_handoff_bundle_ci_policy.py --require-trust-policy --require-redaction-policy --format text` when the target repo needs a checked-in CI policy that declares which bundle policy files must exist.
20. Run `python ../shared/scripts/validate_handoff_bundle_ci_policy.py --format text` before relying on the checked-in CI policy.
21. Run `python ../shared/scripts/run_handoff_ci_checks.py --format text` when you need the same compile, trust-policy, redaction-policy, CI-policy, and smoke checks CI will enforce.
22. Store the checked-in repo policy at `<test_documentation_root>/handoff-bundle-trust-policy.json` when bundle imports must follow fixed signer, age, lease, ownership, or profile-based environment rules.
23. Store the checked-in redaction policy at `<test_documentation_root>/handoff-bundle-redaction-policy.json` when exported bundles must follow fixed path, keyword, or regex redaction rules.
24. Store the checked-in CI policy at `<test_documentation_root>/handoff-bundle-ci-policy.json` when CI should fail if required bundle policy files are missing.
25. Run `python ../shared/scripts/manage_handoff_lease.py release --holder <actor> --format text` when you need to release the lease without the end-of-session wrapper.
26. When the task is incomplete, also create or update the latest session-state file.
27. Keep the handover status and session-state status identical.
28. Link the latest session-state file from the handover when one exists, and keep the pointer in forward-slash form.
29. Create or refresh the handover again if the task status materially changes before transfer.

## 9. Troubleshoot when the handover is unsafe to use

1. Open [references/troubleshooting.md](references/troubleshooting.md) when `CURRENT.md` is missing, statuses conflict, links are stale, validation evidence is absent, the workspace audit reports partial history, the workspace repair command cannot resolve the drift safely, the live lease is stale or conflicting, or the resume instructions are not actionable.
