# Session-State Conflict Resolution

Use this guide when `CURRENT.md` and the linked handover disagree.

## 1. Resolve conflicts in this order

1. Use concrete evidence first:
   - working tree state
   - generated files
   - logs, traces, and screenshots
   - test results and reports
2. Use the newer document next, based on `Last updated`, only when concrete evidence does not settle the conflict.
3. Prefer `python ../shared/scripts/reconcile_handoff_pair.py --handover <handover.md> --session-state <CURRENT.md> --updated-by <actor>` when the conflict can be resolved from the documents themselves.
4. Update both files after the decision so they converge again.

## 2. Authority matrix

- Trust `CURRENT.md` for:
  - active `Status`
  - `Current step`
  - `Remaining steps`
  - `Next owner`
  - `Files touched`
  - `Commands to resume`
- Trust the handover for:
  - `Task summary`
  - `What was done`
  - `Validation status`
  - `Patterns used`
  - `Anti-patterns used`
  - `Strengths of the changes`
  - `Weaknesses of the changes`
  - `How things could be improved`
  - `Files added or modified`

## 3. Status resolution rules

1. Keep `done` only when:
   - remaining work is empty
   - blockers are absent
   - `Next owner` is `None`
2. Change both files to `ready-for-review` when implementation is complete but review or confirmation is still pending.
3. Change both files to `in-progress` when active execution is still happening.
4. Change both files to `blocked` when progress cannot continue without an external dependency or decision.

## 4. Required cleanup after resolution

1. Update `Status` in both files.
2. Update `Last updated`, `Updated by`, and `Next owner` in both files.
3. Fix the handover pointer and session-state pointer if either link is stale.
4. Re-run both validators, or let `reconcile_handoff_pair.py` do it for you.
