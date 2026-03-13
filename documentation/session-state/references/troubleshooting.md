# Session-State Troubleshooting

Use this guide when `CURRENT.md` is missing, stale, or unreliable as the live resume pointer.

## 1. `CURRENT.md` does not exist

- Detect:
  - The task is active but `<test_documentation_root>/session-state/CURRENT.md` is absent.
- Fix:
  1. Create `CURRENT.md` from the latest handover, repo diff, and most recent validation evidence.
  2. Populate every required section from the session-state template.
  3. Link the latest handover in `Handover pointer`.

## 2. `CURRENT.md` is stale

- Detect:
  - The repo changed after the last session-state update.
  - The latest handover or validation artifact is newer than `CURRENT.md`.
- Fix:
  1. Reconcile `Last completed step`, `Current step`, `Remaining steps`, and `Files touched` with the latest truth.
  2. Remove stale statements rather than appending contradictory notes.
  3. Refresh the handover pointer if a newer handover exists.

## 3. Status value is invalid or non-canonical

- Detect:
  - The status is not one of `not-started`, `in-progress`, `blocked`, `ready-for-review`, `done`.
- Fix:
  1. Replace the invalid value with the matching canonical status.
  2. Update the handover document to the same status if it differs.

## 4. Status says `in-progress` but no next action is present

- Detect:
  - `Current step` is empty and `Remaining steps` does not identify the next executable action.
- Fix:
  1. Write the current or next concrete action.
  2. Add the exact file path or command required to continue.

## 5. Status says `blocked` but the unblock requirement is missing

- Detect:
  - The file says `blocked` without naming the dependency, decision, or missing access.
- Fix:
  1. Record the blocker.
  2. Record what is needed to unblock it.
  3. Add the first step to resume once the blocker is resolved.

## 6. Handover pointer is stale or broken

- Detect:
  - `Handover pointer` references a file that does not exist or describes a different task state.
  - `Handover pointer` uses Windows-style backslashes instead of forward slashes.
- Fix:
  1. Link the newest valid handover for the same task with a forward-slash relative path.
  2. If no valid handover exists, create one before ending the session.

## 7. Session-state file and handover disagree

- Detect:
  - `CURRENT.md` and the linked handover disagree on status, next owner, or the next executable action.
- Fix:
  1. Read [conflict-resolution.md](conflict-resolution.md).
  2. Compare repo state, artifacts, timestamps, and linked pointers.
  3. Reconcile both files using the authority matrix.
  4. Re-run both validators.

## 8. Validation snapshot cannot be trusted

- Detect:
  - The validation section is empty, contradictory, or unsupported by artifacts.
- Fix:
  1. Re-run the relevant checks if feasible.
  2. If not feasible, mark them clearly as not run or stale.
  3. Link the most recent reports, logs, traces, or screenshots.

## 9. Files touched list does not match the repo

- Detect:
  - Important edited files are missing, or listed files do not exist.
- Fix:
  1. Reconcile the list against the actual working tree.
  2. Remove nonexistent paths.
  3. Add files that the next operator must inspect first.

## 10. Ownership or freshness fields are missing or stale

- Detect:
  - `Last updated`, `Updated by`, or `Next owner` is missing.
  - The timestamp is not in ISO 8601 format with timezone.
  - The task state changed but `CURRENT.md` still shows an old owner or timestamp.
- Fix:
  1. Update `Last updated` to the current timestamp.
  2. Record the real human or agent identifier in `Updated by`.
  3. Record the real next actor in `Next owner`, or `None` only when status is `done`.

## 11. Live lease is stale, missing, or conflicting

- Detect:
  - Another operator claims they are actively editing the live pair.
  - `python ../shared/scripts/manage_handoff_lease.py show --format text` reports an active or expired lease.
  - The lease holder does not match the human or AI currently changing `CURRENT.md`.
- Fix:
  1. Run `python ../shared/scripts/manage_handoff_lease.py show --format text` to inspect the current lease.
  2. If the lease is expired or invalid, replace it with `claim --force` only after confirming the previous holder is no longer editing.
  3. If another valid holder still owns the lease, stop editing and coordinate the transfer before continuing.
  4. Release the lease with `release --holder <actor>` when the next operator should take over.
