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

from resolve_latest_handoff_pair import resolve_latest_pair  # type: ignore  # noqa: E402
from validate_handoff_pair import (  # type: ignore  # noqa: E402
    discover_handover_path,
    discover_session_state_path,
)
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    REQUIRED_SECTIONS as HANDOVER_SECTIONS,
    extract_next_owner as extract_handover_next_owner,
    extract_status as extract_handover_status,
    normalize_value as handover_normalize,
    parse_sections as parse_handover_sections,
    validate_document as validate_handover_document,
)
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    REQUIRED_SECTIONS as SESSION_SECTIONS,
    extract_next_owner as extract_session_next_owner,
    extract_status as extract_session_status,
    normalize_value as session_normalize,
    parse_sections as parse_session_sections,
    validate_document as validate_session_document,
)


VALID_STATUSES = ("not-started", "in-progress", "blocked", "ready-for-review", "done")


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_markdown(path: Path, expected_root: str, parser) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    root_heading, sections, _ = parser(text)
    if root_heading != expected_root:
        raise ValueError(f"Unexpected root heading in {path}: {root_heading!r}")
    return sections


def write_markdown(path: Path, root_heading: str, ordered_sections: list[str], sections: dict[str, str]) -> None:
    parts = [root_heading, ""]
    for section in ordered_sections:
        parts.append(f"## {section}")
        parts.append(sections[section].rstrip())
        parts.append("")
    path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


def is_none_value(value: str | None) -> bool:
    if value is None:
        return True
    normalized = value.strip().strip("`")
    return not normalized or normalized.lower() == "none"


def first_nonempty_line(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line:
            return line
    return ""


def numbered_values(text: str) -> list[str]:
    values: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        prefix, _, remainder = line.partition(". ")
        if prefix.isdigit():
            value = handover_normalize(remainder.strip())
            if not is_none_value(value):
                values.append(value)
    return values


def bullet_values(text: str) -> list[str]:
    values: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            value = handover_normalize(line[2:].strip())
            if not is_none_value(value):
                values.append(value)
    return values


def render_numbered(items: list[str], default: str = "None") -> str:
    if not items:
        return f"1. {default}"
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def render_bullets(items: list[str], default: str = "None") -> str:
    if not items:
        return f"- {default}"
    return "\n".join(f"- {item}" for item in items)


def parse_resume_instructions(text: str) -> tuple[str, str, str]:
    first_file = "None"
    next_command = "None"
    prerequisites = "None"

    lines = [line.rstrip() for line in text.splitlines()]
    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        if line.startswith("- First file to open:"):
            first_file = handover_normalize(line.split(":", 1)[1].strip())
        elif line.startswith("- Next command to run:"):
            next_command = handover_normalize(line.split(":", 1)[1].strip())
        elif line.startswith("- Prerequisites:") and index + 1 < len(lines):
            following = lines[index + 1].strip()
            prerequisites = following or "None"

    return first_file, next_command, prerequisites


def render_resume_instructions(first_file: str, next_command: str, prerequisites: str) -> str:
    return (
        f"- First file to open: `{first_file}`\n"
        f"- Next command to run: `{next_command}`\n"
        f"- Prerequisites:\n"
        f"  {prerequisites}"
    )


def parse_session_blockers(text: str) -> tuple[str, str]:
    blocker = "None"
    needed_to_unblock = "None"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- Needed to unblock:"):
            needed_to_unblock = line.split(":", 1)[1].strip() or "None"
        elif line.startswith("- "):
            candidate = handover_normalize(line[2:].strip())
            if not candidate.lower().startswith("needed to unblock:") and not is_none_value(candidate):
                blocker = candidate

    return blocker, needed_to_unblock


def render_session_blockers(blocker: str, needed_to_unblock: str) -> str:
    if is_none_value(blocker):
        return "- None"
    if is_none_value(needed_to_unblock):
        return f"- {blocker}"
    return f"- {blocker}\n- Needed to unblock: {needed_to_unblock}"


def parse_handover_blockers_and_decisions(text: str) -> tuple[str, str, str]:
    blocker = "None"
    decision = "None"
    assumption = "None"
    lines = [line.strip() for line in text.splitlines()]

    for index, line in enumerate(lines):
        if line == "- Blockers:" and index + 1 < len(lines):
            blocker = lines[index + 1] or "None"
        elif line == "- Decisions:" and index + 1 < len(lines):
            decision = lines[index + 1] or "None"
        elif line == "- Assumptions:" and index + 1 < len(lines):
            assumption = lines[index + 1] or "None"

    return blocker.strip(), decision.strip(), assumption.strip()


def parse_decisions_and_assumptions(text: str) -> tuple[str, str]:
    decision = "None"
    assumption = "None"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- Decision:"):
            decision = line.split(":", 1)[1].strip() or "None"
        elif line.startswith("- Assumption:"):
            assumption = line.split(":", 1)[1].strip() or "None"
    return decision, assumption


def render_handover_blockers_and_decisions(blocker: str, decision: str, assumption: str) -> str:
    return (
        "- Blockers:\n"
        f"  {blocker}\n"
        "- Decisions:\n"
        f"  {decision}\n"
        "- Assumptions:\n"
        f"  {assumption}"
    )


def relative_pointer(from_path: Path, to_path: Path) -> str:
    return Path(os.path.relpath(to_path.resolve(), start=from_path.resolve().parent)).as_posix()


def choose_primary_or_fallback(primary: str, fallback: str, normalizer) -> str:
    primary_value = normalizer(first_nonempty_line(primary))
    if not is_none_value(primary_value):
        return primary_value
    fallback_value = normalizer(first_nonempty_line(fallback))
    if not is_none_value(fallback_value):
        return fallback_value
    return "None"


def derive_status(
    handover_sections: dict[str, str],
    session_sections: dict[str, str],
    explicit_status: str | None,
    explicit_next_owner: str | None,
) -> str:
    if explicit_status:
        return explicit_status

    handover_status = extract_handover_status(handover_sections)
    session_status = extract_session_status(session_sections)
    remaining_steps = numbered_values(session_sections["Remaining steps"]) or numbered_values(handover_sections["Remaining work"])
    session_blocker, _ = parse_session_blockers(session_sections["Blockers"])
    handover_blocker, _, _ = parse_handover_blockers_and_decisions(handover_sections["Blockers and decisions"])
    blockers_present = not is_none_value(session_blocker) or not is_none_value(handover_blocker)
    current_next_owner = explicit_next_owner or extract_session_next_owner(session_sections) or extract_handover_next_owner(handover_sections)

    if session_status == "done":
        if remaining_steps or blockers_present or not is_none_value(current_next_owner) or handover_status != "done":
            if blockers_present:
                return "blocked"
            if remaining_steps:
                return "in-progress"
            return "ready-for-review"
        return "done"

    if blockers_present or session_status == "blocked" or handover_status == "blocked":
        return "blocked"

    if session_status in {"not-started", "in-progress", "ready-for-review"}:
        return session_status

    if handover_status == "done" and not remaining_steps and is_none_value(current_next_owner):
        return "done"

    return handover_status


def reconcile_pair(
    handover_path: Path,
    session_path: Path,
    updated_by: str,
    explicit_next_owner: str | None,
    explicit_status: str | None,
) -> tuple[str, str]:
    handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
    session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)

    status = derive_status(handover_sections, session_sections, explicit_status, explicit_next_owner)
    now = iso_now()

    resolved_next_owner = explicit_next_owner or extract_session_next_owner(session_sections) or extract_handover_next_owner(handover_sections)
    if status == "done":
        resolved_next_owner = "None"
    elif is_none_value(resolved_next_owner):
        resolved_next_owner = updated_by

    task_summary = handover_sections["Task summary"].strip() or session_sections["Task"].strip()
    current_step = choose_primary_or_fallback(session_sections["Current step"], handover_sections["Current step"], session_normalize)
    remaining_steps = numbered_values(session_sections["Remaining steps"]) or numbered_values(handover_sections["Remaining work"])
    files_touched = bullet_values(session_sections["Files touched"])
    commands_to_resume = bullet_values(session_sections["Commands to resume"])
    first_file, next_command, prerequisites = parse_resume_instructions(handover_sections["Resume instructions"])
    if files_touched:
        first_file = files_touched[0]
    if commands_to_resume:
        next_command = commands_to_resume[0]

    session_blocker, needed_to_unblock = parse_session_blockers(session_sections["Blockers"])
    handover_blocker, handover_decision, handover_assumption = parse_handover_blockers_and_decisions(handover_sections["Blockers and decisions"])
    blocker = session_blocker if not is_none_value(session_blocker) else handover_blocker
    decision, assumption = parse_decisions_and_assumptions(session_sections["Decisions and assumptions"])
    if is_none_value(decision):
        decision = handover_decision
    if is_none_value(assumption):
        assumption = handover_assumption

    handover_sections["Task summary"] = task_summary
    handover_sections["Status"] = status
    handover_sections["Last updated"] = now
    handover_sections["Updated by"] = updated_by
    handover_sections["Next owner"] = resolved_next_owner
    handover_sections["Current step"] = current_step
    handover_sections["Remaining work"] = render_numbered(remaining_steps)
    handover_sections["Resume instructions"] = render_resume_instructions(first_file, next_command, prerequisites)
    handover_sections["Blockers and decisions"] = render_handover_blockers_and_decisions(blocker, decision, assumption)
    handover_sections["Session-state pointer"] = "None" if status == "done" else relative_pointer(handover_path, session_path)

    session_sections["Task"] = task_summary
    session_sections["Status"] = status
    session_sections["Last updated"] = now
    session_sections["Updated by"] = updated_by
    session_sections["Next owner"] = resolved_next_owner
    session_sections["Current step"] = current_step
    session_sections["Remaining steps"] = render_numbered(remaining_steps)
    session_sections["Files touched"] = render_bullets(files_touched)
    session_sections["Commands to resume"] = render_bullets(commands_to_resume)
    session_sections["Blockers"] = render_session_blockers(blocker, needed_to_unblock)
    session_sections["Handover pointer"] = relative_pointer(session_path, handover_path)

    write_markdown(handover_path, HANDOVER_ROOT, HANDOVER_SECTIONS, handover_sections)
    write_markdown(session_path, SESSION_ROOT, SESSION_SECTIONS, session_sections)

    handover_errors = validate_handover_document(handover_path)
    session_errors = validate_session_document(session_path)
    if handover_errors or session_errors:
        details = "\n".join(
            [*(f"HANDOVER: {error}" for error in handover_errors), *(f"SESSION: {error}" for error in session_errors)]
        )
        raise ValueError(f"Reconciled files did not validate:\n{details}")

    return status, resolved_next_owner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconcile a handover and session-state pair deterministically.")
    parser.add_argument("--handover", help="Path to the handover markdown file.")
    parser.add_argument("--session-state", help="Path to the session-state markdown file.")
    parser.add_argument("--updated-by", required=True, help="Identifier for the human or AI performing reconciliation.")
    parser.add_argument("--next-owner", help="Optional explicit next owner override.")
    parser.add_argument("--status", choices=VALID_STATUSES, help="Optional explicit status override.")
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
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not handover_path.exists():
        print(f"Handover file does not exist: {handover_path}", file=sys.stderr)
        return 1
    if not session_path.exists():
        print(f"Session-state file does not exist: {session_path}", file=sys.stderr)
        return 1

    try:
        status, next_owner = reconcile_pair(
            handover_path=handover_path,
            session_path=session_path,
            updated_by=args.updated_by,
            explicit_next_owner=args.next_owner,
            explicit_status=args.status,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Reconciled pair: status={status}, next_owner={next_owner}")
    print(f"Handover: {handover_path}")
    print(f"Session-state: {session_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
