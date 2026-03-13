#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

SHARED_SCRIPTS = Path(__file__).resolve().parents[2] / "shared" / "scripts"
if str(SHARED_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SHARED_SCRIPTS))

from resolve_test_docs_root import resolve_docs_root


VALID_STATUSES = ("not-started", "in-progress", "blocked", "ready-for-review", "done")


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def numbered_list(items: list[str]) -> str:
    if not items:
        return "1. None"
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def build_output_path(root: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return root / "handovers" / f"{timestamp}_handover.md"


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def normalize_pointer(pointer: str) -> str:
    if pointer.strip().lower() == "none":
        return "None"
    return Path(pointer).as_posix()


def render_document(args: argparse.Namespace, session_state_pointer: str, last_updated: str) -> str:
    return f"""# Handover

## Task summary
{args.task_summary}

## Status
{args.status}

## Last updated
{last_updated}

## Updated by
{args.updated_by}

## Next owner
{args.next_owner}

## What was done
{bullet_list(args.what_was_done)}

## Last completed step
{args.last_completed_step}

## Current step
{args.current_step}

## Remaining work
{numbered_list(args.remaining_work)}

## Blockers and decisions
- Blockers:
  None
- Decisions:
  None
- Assumptions:
  None

## Validation status
- Passed:
  None
- Failed:
  None
- Not run:
  None

## Resume instructions
- First file to open: `{args.first_file}`
- Next command to run: `{args.next_command}`
- Prerequisites:
  None

## Skills and subskills used
- None

## Non-skill actions and suggestions
- None

## Patterns used
- None

## Anti-patterns used
- None

## Strengths of the changes
- None

## Weaknesses of the changes
- None

## How things could be improved
- None

## Files added or modified
- Documentation:
  - None
- POMs:
  - None
- Test Scripts:
  - None
- Configurations:
  - None
- Other:
  - None

## Session-state pointer
{session_state_pointer}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a deterministic handover markdown file.")
    parser.add_argument("--root", help="Optional explicit documentation root. Auto-discovered when omitted.")
    parser.add_argument("--task-summary", required=True, help="Short summary of the task goal.")
    parser.add_argument("--status", choices=VALID_STATUSES, default="in-progress", help="Canonical task status.")
    parser.add_argument("--updated-by", required=True, help="Identifier for the human or AI updating the handover.")
    parser.add_argument(
        "--next-owner",
        required=True,
        help="Identifier for the next actor, or None when the status is done.",
    )
    parser.add_argument(
        "--last-updated",
        default=current_timestamp(),
        help="ISO 8601 timestamp with timezone. Defaults to the current local time.",
    )
    parser.add_argument(
        "--what-was-done",
        action="append",
        default=[],
        help="Repeat for each completed action.",
    )
    parser.add_argument("--last-completed-step", default="None", help="Last fully completed action.")
    parser.add_argument("--current-step", default="None", help="Current in-progress action.")
    parser.add_argument(
        "--remaining-work",
        action="append",
        default=[],
        help="Repeat for each remaining action.",
    )
    parser.add_argument("--first-file", default="None", help="First file to open when resuming.")
    parser.add_argument("--next-command", default="None", help="Next command to run when resuming.")
    parser.add_argument(
        "--session-state-pointer",
        help="Optional path to CURRENT.md or a session-state snapshot. Defaults to ../session-state/CURRENT.md for non-done work.",
    )
    parser.add_argument("--output", help="Optional explicit output path.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output file if it exists.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = resolve_docs_root(explicit_root=args.root)
    output_path = Path(args.output) if args.output else build_output_path(root)

    if output_path.exists() and not args.force:
        print(f"Refusing to overwrite existing file: {output_path}", file=sys.stderr)
        return 1

    if args.session_state_pointer is not None:
        session_state_pointer = normalize_pointer(args.session_state_pointer)
    elif args.status == "done":
        session_state_pointer = "None"
    else:
        session_state_pointer = "../session-state/CURRENT.md"

    if args.status == "done":
        args.next_owner = "None"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.status != "done":
        (root / "session-state").mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_document(args, session_state_pointer, args.last_updated), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
