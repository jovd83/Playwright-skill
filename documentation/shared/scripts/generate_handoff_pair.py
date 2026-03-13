#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"
HANDOVER_SCRIPTS = REPO_ROOT / "documentation" / "handover" / "scripts"
SESSION_SCRIPTS = REPO_ROOT / "documentation" / "session-state" / "scripts"

for script_dir in (SHARED_SCRIPTS, HANDOVER_SCRIPTS, SESSION_SCRIPTS):
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

from generate_handover import (  # type: ignore  # noqa: E402
    build_output_path as build_handover_output_path,
    render_document as render_handover_document,
)
from generate_session_state import render_document as render_session_document  # type: ignore  # noqa: E402
from resolve_test_docs_root import resolve_docs_root  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    parse_sections as parse_handover_sections,
    validate_document as validate_handover_document,
)
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    parse_sections as parse_session_sections,
    validate_document as validate_session_document,
)
from validate_handoff_pair import collect_pair_errors  # type: ignore  # noqa: E402


VALID_STATUSES = ("not-started", "in-progress", "blocked", "ready-for-review", "done")


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def relative_pointer(from_path: Path, to_path: Path) -> str:
    return Path(os.path.relpath(to_path.resolve(), start=from_path.resolve().parent)).as_posix()


def parse_markdown(path: Path, expected_root: str, parser) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    root_heading, sections, _ = parser(text)
    if root_heading != expected_root:
        raise ValueError(f"Unexpected root heading in {path}: {root_heading!r}")
    return sections


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a linked handover/session-state pair with one timestamp.")
    parser.add_argument("--root", help="Optional explicit documentation root. Auto-discovered when omitted.")
    parser.add_argument("--task", required=True, help="Task description shared by the handover and session-state file.")
    parser.add_argument("--status", choices=VALID_STATUSES, default="in-progress", help="Canonical shared task status.")
    parser.add_argument("--updated-by", required=True, help="Identifier for the human or AI creating the pair.")
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
        "--what-was-done",
        action="append",
        default=[],
        help="Repeat for each completed action to include in the handover.",
    )
    parser.add_argument(
        "--blocker",
        dest="blockers",
        action="append",
        default=[],
        help="Repeat for each active blocker to include in the session-state file.",
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
        help="Repeat for each command the next operator should run.",
    )
    parser.add_argument("--first-file", help="Optional explicit first file to open in handover resume instructions.")
    parser.add_argument("--next-command", help="Optional explicit next command in handover resume instructions.")
    parser.add_argument(
        "--handover-output",
        help="Optional explicit output path for the handover markdown file.",
    )
    parser.add_argument(
        "--session-output",
        help="Optional explicit output path for the session-state markdown file.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing output files if they already exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = resolve_docs_root(explicit_root=args.root)
    handover_path = Path(args.handover_output) if args.handover_output else build_handover_output_path(root)
    session_path = Path(args.session_output) if args.session_output else root / "session-state" / "CURRENT.md"

    if handover_path.resolve() == session_path.resolve():
        print("Handover output and session-state output must be different files.", file=sys.stderr)
        return 1

    for path in (handover_path, session_path):
        if path.exists() and not args.force:
            print(f"Refusing to overwrite existing file: {path}", file=sys.stderr)
            return 1

    next_owner = "None" if args.status == "done" else args.next_owner
    first_file = args.first_file or (args.files_touched[0] if args.files_touched else "None")
    next_command = args.next_command or (args.commands_to_resume[0] if args.commands_to_resume else "None")

    handover_pointer = relative_pointer(session_path, handover_path)
    session_pointer = relative_pointer(handover_path, session_path)

    handover_args = argparse.Namespace(
        task_summary=args.task,
        status=args.status,
        updated_by=args.updated_by,
        next_owner=next_owner,
        what_was_done=args.what_was_done,
        last_completed_step=args.last_completed_step,
        current_step=args.current_step,
        remaining_work=args.remaining_steps,
        first_file=first_file,
        next_command=next_command,
    )
    session_args = argparse.Namespace(
        task=args.task,
        status=args.status,
        updated_by=args.updated_by,
        next_owner=next_owner,
        last_completed_step=args.last_completed_step,
        current_step=args.current_step,
        remaining_steps=args.remaining_steps,
        blockers=args.blockers,
        files_touched=args.files_touched,
        commands_to_resume=args.commands_to_resume,
    )

    handover_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    handover_path.write_text(
        render_handover_document(handover_args, session_pointer, args.last_updated),
        encoding="utf-8",
    )
    session_path.write_text(
        render_session_document(session_args, handover_pointer, args.last_updated),
        encoding="utf-8",
    )

    errors: list[str] = []
    errors.extend(f"HANDOVER: {error}" for error in validate_handover_document(handover_path))
    errors.extend(f"SESSION: {error}" for error in validate_session_document(session_path))

    if not errors:
        try:
            handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
            session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        errors.extend(
            f"PAIR: {error}"
            for error in collect_pair_errors(
                handover_path=handover_path,
                session_path=session_path,
                handover_sections=handover_sections,
                session_sections=session_sections,
            )
        )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Generated handoff pair: status={args.status}, next_owner={next_owner}")
    print(f"Handover: {handover_path}")
    print(f"Session-state: {session_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
