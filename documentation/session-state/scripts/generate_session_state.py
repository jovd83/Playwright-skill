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


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def normalize_pointer(pointer: str) -> str:
    if pointer.strip().lower() == "none":
        return "None"
    return Path(pointer).as_posix()


def render_document(args: argparse.Namespace, handover_pointer: str, last_updated: str) -> str:
    return f"""# Session State

## Task
{args.task}

## Status
{args.status}

## Last updated
{last_updated}

## Updated by
{args.updated_by}

## Next owner
{args.next_owner}

## Last completed step
{args.last_completed_step}

## Current step
{args.current_step}

## Remaining steps
{numbered_list(args.remaining_steps)}

## Blockers
{bullet_list(args.blockers)}

## Decisions and assumptions
- Decision: None
- Assumption: None

## Files touched
{bullet_list(args.files_touched)}

## Commands to resume
{bullet_list(args.commands_to_resume)}

## Validation snapshot
- Passed:
  None
- Failed:
  None
- Skipped:
  None

## Artifacts
- None

## Handover pointer
{handover_pointer}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a deterministic session-state markdown file.")
    parser.add_argument("--root", help="Optional explicit documentation root. Auto-discovered when omitted.")
    parser.add_argument("--task", required=True, help="One-sentence task description.")
    parser.add_argument("--status", choices=VALID_STATUSES, default="in-progress", help="Canonical task status.")
    parser.add_argument("--updated-by", required=True, help="Identifier for the human or AI updating the file.")
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
    parser.add_argument("--last-completed-step", default="None", help="Last fully completed action.")
    parser.add_argument("--current-step", default="None", help="Current in-progress action.")
    parser.add_argument(
        "--remaining-step",
        dest="remaining_steps",
        action="append",
        default=[],
        help="Repeat for each remaining action.",
    )
    parser.add_argument(
        "--blocker",
        dest="blockers",
        action="append",
        default=[],
        help="Repeat for each blocker.",
    )
    parser.add_argument(
        "--file-touched",
        dest="files_touched",
        action="append",
        default=[],
        help="Repeat for each file that the next operator should inspect.",
    )
    parser.add_argument(
        "--command-to-resume",
        dest="commands_to_resume",
        action="append",
        default=[],
        help="Repeat for each resume command.",
    )
    parser.add_argument("--handover-pointer", default="None", help="Optional path to the latest handover.")
    parser.add_argument("--output", help="Optional explicit output path. Defaults to <root>/session-state/CURRENT.md.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output file if it exists.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = resolve_docs_root(explicit_root=args.root)
    output_path = Path(args.output) if args.output else root / "session-state" / "CURRENT.md"

    if output_path.exists() and not args.force:
        print(f"Refusing to overwrite existing file: {output_path}", file=sys.stderr)
        return 1

    args.handover_pointer = normalize_pointer(args.handover_pointer)

    if args.status == "done":
        args.next_owner = "None"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.handover_pointer != "None":
        (root / "handovers").mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_document(args, args.handover_pointer, args.last_updated), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
