#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
HANDOVER_SCRIPTS = REPO_ROOT / "documentation" / "handover" / "scripts"
SESSION_SCRIPTS = REPO_ROOT / "documentation" / "session-state" / "scripts"
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"

for script_dir in (HANDOVER_SCRIPTS, SESSION_SCRIPTS, SHARED_SCRIPTS):
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

from reconcile_handoff_pair import (  # type: ignore  # noqa: E402
    bullet_values,
    numbered_values,
    parse_handover_blockers_and_decisions,
    parse_resume_instructions,
    parse_session_blockers,
    relative_pointer,
    render_bullets,
    render_handover_blockers_and_decisions,
    render_numbered,
    render_resume_instructions,
    render_session_blockers,
    write_markdown,
)
from resolve_latest_handoff_pair import resolve_latest_pair  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    REQUIRED_SECTIONS as HANDOVER_SECTIONS,
    extract_next_owner as extract_handover_next_owner,
    extract_status as extract_handover_status,
    parse_sections as parse_handover_sections,
    validate_document as validate_handover_document,
)
from validate_handoff_pair import (  # type: ignore  # noqa: E402
    collect_pair_errors,
    discover_handover_path,
    discover_session_state_path,
    parse_markdown,
)
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    REQUIRED_SECTIONS as SESSION_SECTIONS,
    extract_next_owner as extract_session_next_owner,
    extract_status as extract_session_status,
    parse_sections as parse_session_sections,
    validate_document as validate_session_document,
)


VALID_STATUSES = ("not-started", "in-progress", "blocked", "ready-for-review", "done")


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def normalize_list(items: list[str] | None) -> list[str]:
    if not items:
        return []
    normalized = [item.strip() for item in items if item.strip()]
    if len(normalized) == 1 and normalized[0].lower() == "none":
        return []
    return normalized


def choose_scalar(explicit: str | None, current: str) -> str:
    if explicit is None:
        return current
    stripped = explicit.strip()
    return stripped or "None"


def choose_list(explicit: list[str] | None, current: list[str]) -> list[str]:
    if explicit is None:
        return current
    return normalize_list(explicit)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update a linked handover/session-state pair in place.")
    parser.add_argument("--handover", help="Path to the handover markdown file.")
    parser.add_argument("--session-state", help="Path to the session-state markdown file.")
    parser.add_argument("--updated-by", required=True, help="Identifier for the human or AI updating the pair.")
    parser.add_argument(
        "--last-updated",
        default=current_timestamp(),
        help="ISO 8601 timestamp with timezone. Defaults to the current local time.",
    )
    parser.add_argument("--task", help="Optional replacement for the shared task summary.")
    parser.add_argument("--status", choices=VALID_STATUSES, help="Optional replacement for the shared status.")
    parser.add_argument("--next-owner", help="Optional replacement for the shared next owner.")
    parser.add_argument("--last-completed-step", help="Optional replacement for the last completed step.")
    parser.add_argument("--current-step", help="Optional replacement for the current step.")
    parser.add_argument("--first-file", help="Optional replacement for the first file to open.")
    parser.add_argument("--next-command", help="Optional replacement for the next command to run.")
    parser.add_argument("--decision", help="Optional replacement for the recorded decision.")
    parser.add_argument("--assumption", help="Optional replacement for the recorded assumption.")
    parser.add_argument(
        "--what-was-done",
        action="append",
        help="Repeat to replace the handover What was done list. Pass a single value of None to clear.",
    )
    parser.add_argument(
        "--remaining-step",
        dest="remaining_steps",
        action="append",
        help="Repeat to replace the remaining steps list. Pass a single value of None to clear.",
    )
    parser.add_argument(
        "--blocker",
        dest="blockers",
        action="append",
        help="Repeat to replace the blocker list. Pass a single value of None to clear.",
    )
    parser.add_argument(
        "--file-touched",
        dest="files_touched",
        action="append",
        help="Repeat to replace the files touched list. Pass a single value of None to clear.",
    )
    parser.add_argument(
        "--command-to-resume",
        dest="commands_to_resume",
        action="append",
        help="Repeat to replace the resume command list. Pass a single value of None to clear.",
    )
    parser.add_argument(
        "--prerequisite",
        dest="prerequisites",
        action="append",
        help="Repeat to replace the prerequisites list. Pass a single value of None to clear.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if not args.handover and not args.session_state:
            _, handover_path, session_path, _ = resolve_latest_pair(start_dir=Path.cwd())
        else:
            handover_path = Path(args.handover) if args.handover else None
            session_path = Path(args.session_state) if args.session_state else None

            if handover_path is not None and not handover_path.exists():
                print(f"Handover file does not exist: {handover_path}", file=sys.stderr)
                return 1
            if session_path is not None and not session_path.exists():
                print(f"Session-state file does not exist: {session_path}", file=sys.stderr)
                return 1

            if handover_path is None:
                handover_path = discover_handover_path(session_path)
            if session_path is None:
                session_path = discover_session_state_path(handover_path)

        handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
        session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    task = choose_scalar(args.task, handover_sections["Task summary"].strip() or session_sections["Task"].strip())
    status = args.status or extract_session_status(session_sections) or extract_handover_status(handover_sections)
    next_owner = args.next_owner or extract_session_next_owner(session_sections) or extract_handover_next_owner(handover_sections)
    if status == "done":
        next_owner = "None"

    last_completed_step = choose_scalar(args.last_completed_step, session_sections["Last completed step"].strip())
    current_step = choose_scalar(args.current_step, session_sections["Current step"].strip())
    remaining_steps = choose_list(args.remaining_steps, numbered_values(session_sections["Remaining steps"]) or numbered_values(handover_sections["Remaining work"]))
    what_was_done = choose_list(args.what_was_done, bullet_values(handover_sections["What was done"]))
    files_touched = choose_list(args.files_touched, bullet_values(session_sections["Files touched"]))
    commands_to_resume = choose_list(args.commands_to_resume, bullet_values(session_sections["Commands to resume"]))

    current_first_file, current_next_command, current_prerequisites_text = parse_resume_instructions(handover_sections["Resume instructions"])
    current_prerequisites = normalize_list([current_prerequisites_text]) if current_prerequisites_text != "None" else []
    first_file = choose_scalar(args.first_file, current_first_file)
    next_command = choose_scalar(args.next_command, current_next_command)
    prerequisites = choose_list(args.prerequisites, current_prerequisites)

    current_blocker, current_needed_to_unblock = parse_session_blockers(session_sections["Blockers"])
    blockers = choose_list(args.blockers, [] if current_blocker == "None" else [current_blocker])
    needed_to_unblock = current_needed_to_unblock

    _, current_decision, current_assumption = parse_handover_blockers_and_decisions(handover_sections["Blockers and decisions"])
    decision = choose_scalar(args.decision, current_decision)
    assumption = choose_scalar(args.assumption, current_assumption)

    handover_sections["Task summary"] = task
    handover_sections["Status"] = status
    handover_sections["Last updated"] = args.last_updated
    handover_sections["Updated by"] = args.updated_by
    handover_sections["Next owner"] = next_owner
    handover_sections["What was done"] = render_bullets(what_was_done)
    handover_sections["Last completed step"] = last_completed_step
    handover_sections["Current step"] = current_step
    handover_sections["Remaining work"] = render_numbered(remaining_steps)
    handover_sections["Blockers and decisions"] = render_handover_blockers_and_decisions(
        "; ".join(blockers) if blockers else "None",
        decision,
        assumption,
    )
    handover_sections["Resume instructions"] = render_resume_instructions(
        first_file,
        next_command,
        "; ".join(prerequisites) if prerequisites else "None",
    )
    handover_sections["Session-state pointer"] = "None" if status == "done" else relative_pointer(handover_path, session_path)

    session_sections["Task"] = task
    session_sections["Status"] = status
    session_sections["Last updated"] = args.last_updated
    session_sections["Updated by"] = args.updated_by
    session_sections["Next owner"] = next_owner
    session_sections["Last completed step"] = last_completed_step
    session_sections["Current step"] = current_step
    session_sections["Remaining steps"] = render_numbered(remaining_steps)
    if blockers:
        blocker_text = blockers[0]
        if needed_to_unblock != "None":
            session_sections["Blockers"] = render_session_blockers(blocker_text, needed_to_unblock)
        else:
            session_sections["Blockers"] = render_bullets(blockers)
    else:
        session_sections["Blockers"] = "- None"
    session_sections["Decisions and assumptions"] = f"- Decision: {decision}\n- Assumption: {assumption}"
    session_sections["Files touched"] = render_bullets(files_touched)
    session_sections["Commands to resume"] = render_bullets(commands_to_resume)
    session_sections["Handover pointer"] = relative_pointer(session_path, handover_path)

    write_markdown(handover_path, HANDOVER_ROOT, HANDOVER_SECTIONS, handover_sections)
    write_markdown(session_path, SESSION_ROOT, SESSION_SECTIONS, session_sections)

    errors: list[str] = []
    errors.extend(f"HANDOVER: {error}" for error in validate_handover_document(handover_path))
    errors.extend(f"SESSION: {error}" for error in validate_session_document(session_path))

    if not errors:
        handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
        session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
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

    print(f"Updated handoff pair: status={status}, next_owner={next_owner}")
    print(f"Handover: {handover_path}")
    print(f"Session-state: {session_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
