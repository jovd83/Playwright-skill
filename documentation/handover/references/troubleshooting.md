# Handover Troubleshooting

Use this guide when the handover document cannot safely transfer work to another operator.

## 1. `CURRENT.md` is missing but the task is not `done`

- Detect:
  - The handover status is `not-started`, `in-progress`, `blocked`, or `ready-for-review`.
  - The linked session-state file does not exist.
- Fix:
  1. Create `<test_documentation_root>/session-state/CURRENT.md`.
  2. Populate it from the latest handover and current repo state.
  3. Add the session-state path back into the handover.

## 2. Handover status and session-state status conflict

- Detect:
  - The handover and `CURRENT.md` use different canonical statuses.
- Fix:
  1. Read [conflict-resolution.md](conflict-resolution.md).
  2. Compare timestamps, recent file changes, and validation evidence.
  3. Determine the status that matches the latest verified task state.
  4. Update both files to the same canonical status.
  5. Add a note in `Blockers and decisions` if the mismatch exposed uncertainty.

## 3. Resume instructions are vague or non-executable

- Detect:
  - The handover lacks a concrete file path, command, or prerequisite.
- Fix:
  1. Identify the exact next file to open.
  2. Record the next command to run exactly as it should be executed.
  3. List missing services, credentials, environment variables, or setup dependencies.

## 4. Validation status is empty or unsupported

- Detect:
  - The handover claims validation happened but provides no command, artifact, or result.
- Fix:
  1. Re-run the relevant validation if feasible.
  2. If re-running is not feasible, mark the validation as `Not run`.
  3. Link logs, reports, traces, or screenshots when they exist.

## 5. Session-state pointer is stale or broken

- Detect:
  - The path in `Session-state pointer` does not exist.
  - The pointed file does not describe the same task.
  - The pointer uses Windows-style backslashes instead of forward slashes.
- Fix:
  1. Find the latest valid `CURRENT.md` or create a new one.
  2. Replace the stale pointer in the handover with a forward-slash relative path.
  3. Remove references to superseded session-state snapshots if they cause confusion.

## 6. Status is `done` but the handover still shows remaining work

- Detect:
  - `Remaining work` contains executable tasks while status is `done`.
- Fix:
  1. Change the status to `ready-for-review` or `in-progress`, whichever matches the true state.
  2. Keep only genuinely outstanding work in `Remaining work`.
  3. Move completed items into `What was done`.

## 7. Status is `blocked` but no unblock path is recorded

- Detect:
  - The handover says `blocked` without naming the blocker or the next dependency.
- Fix:
  1. Record the blocker explicitly.
  2. State what decision, access, input, or fix is required.
  3. Add the first step to take once the blocker is removed.

## 8. File list or artifact paths do not exist

- Detect:
  - Listed files, reports, traces, or screenshots are missing.
- Fix:
  1. Remove incorrect paths.
  2. Replace them with verified absolute or project-relative paths.
  3. Regenerate the missing artifact if it is required for safe resume.

## 9. Ownership or freshness fields are missing or stale

- Detect:
  - `Last updated`, `Updated by`, or `Next owner` is missing.
  - The timestamp is not in ISO 8601 format with timezone.
  - The document was changed but `Last updated` was not refreshed.
- Fix:
  1. Update `Last updated` to the current timestamp.
  2. Record the real human or agent identifier in `Updated by`.
  3. Record the real next actor in `Next owner`, or `None` only when status is `done`.

## 10. Live lease is stale, missing, or conflicting

- Detect:
  - Another operator claims they are actively editing the live pair.
  - `python ../shared/scripts/manage_handoff_lease.py show --format text` reports an active or expired lease.
  - The lease holder does not match the human or AI currently changing the files.
- Fix:
  1. Run `python ../shared/scripts/manage_handoff_lease.py show --format text` to inspect the current lease.
  2. If the lease is expired or invalid, replace it with `claim --force` only after confirming the previous holder is no longer editing.
  3. If another valid holder still owns the lease, stop editing and coordinate the transfer before continuing.
  4. Release the lease with `release --holder <actor>` when the handoff is ready for the next operator.
