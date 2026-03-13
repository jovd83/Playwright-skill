#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"
HANDOVER_SCRIPTS = REPO_ROOT / "documentation" / "handover" / "scripts"
SESSION_SCRIPTS = REPO_ROOT / "documentation" / "session-state" / "scripts"

for script_dir in (SHARED_SCRIPTS, HANDOVER_SCRIPTS, SESSION_SCRIPTS):
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

from handoff_lease import inspect_lease  # type: ignore  # noqa: E402
from resolve_latest_handoff_pair import resolve_latest_pair  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    extract_last_updated as extract_handover_last_updated,
    extract_next_owner as extract_handover_next_owner,
    extract_pointer as extract_handover_pointer,
    extract_status as extract_handover_status,
    extract_updated_by as extract_handover_updated_by,
    parse_sections as parse_handover_sections,
    resolve_pointer as resolve_handover_pointer,
    validate_document as validate_handover_document,
)
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    extract_pointer as extract_session_pointer,
    parse_sections as parse_session_sections,
    resolve_pointer as resolve_session_pointer,
    validate_document as validate_session_document,
)
from validate_handoff_pair import collect_pair_errors  # type: ignore  # noqa: E402


def parse_markdown(path: Path, expected_root: str, parser) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    root_heading, sections, _ = parser(text)
    if root_heading != expected_root:
        raise ValueError(f"Unexpected root heading in {path}: {root_heading!r}")
    return sections


def discover_session_state_path(handover_path: Path) -> Path:
    handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
    pointer = extract_handover_pointer(handover_sections)
    if pointer is None:
        raise ValueError("Handover does not contain a session-state pointer. Pass --session-state explicitly.")
    return resolve_handover_pointer(handover_path, pointer)


def discover_handover_path(session_path: Path) -> Path:
    session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
    pointer = extract_session_pointer(session_sections)
    if pointer is None:
        raise ValueError("Session-state does not contain a handover pointer. Pass --handover explicitly.")
    return resolve_session_pointer(session_path, pointer)


def normalize_line(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("`") and stripped.endswith("`") and len(stripped) >= 2:
        return stripped[1:-1]
    return stripped


def scalar_value(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line:
            if line.startswith("- "):
                line = line[2:].strip()
            return normalize_line(line)
    return "None"


def numbered_values(text: str) -> list[str]:
    values: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        prefix, _, remainder = line.partition(". ")
        if prefix.isdigit():
            value = normalize_line(remainder.strip())
            if value and value.lower() != "none":
                values.append(value)
    return values


def bullet_values(text: str) -> list[str]:
    values: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            value = normalize_line(line[2:].strip())
            if value and value.lower() != "none":
                values.append(value)
    return values


def parse_resume_instructions(text: str) -> tuple[str, str, list[str]]:
    first_file = "None"
    next_command = "None"
    prerequisites: list[str] = []
    lines = text.splitlines()

    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        if line.startswith("- First file to open:"):
            first_file = normalize_line(line.split(":", 1)[1].strip())
        elif line.startswith("- Next command to run:"):
            next_command = normalize_line(line.split(":", 1)[1].strip())
        elif line.startswith("- Prerequisites:"):
            for follow_line in lines[index + 1 :]:
                candidate = follow_line.strip()
                if not candidate:
                    continue
                if candidate.startswith("## "):
                    break
                prerequisite = normalize_line(candidate)
                if prerequisite and prerequisite.lower() != "none":
                    prerequisites.append(prerequisite)
    return first_file, next_command, prerequisites


def parse_blockers(text: str) -> list[str]:
    values: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        value = normalize_line(line[2:].strip())
        if not value or value.lower() == "none":
            continue
        values.append(value)
    return values


def build_summary(
    handover_path: Path,
    session_path: Path,
    handover_sections: dict[str, str],
    session_sections: dict[str, str],
    lease: dict[str, Any],
    warnings: list[str],
) -> dict[str, object]:
    first_file, next_command, prerequisites = parse_resume_instructions(handover_sections["Resume instructions"])
    remaining_steps = numbered_values(session_sections["Remaining steps"]) or numbered_values(handover_sections["Remaining work"])
    what_was_done = bullet_values(handover_sections["What was done"])
    files_touched = bullet_values(session_sections["Files touched"])
    resume_commands = bullet_values(session_sections["Commands to resume"])
    blockers = parse_blockers(session_sections["Blockers"])

    return {
        "task": scalar_value(handover_sections["Task summary"]),
        "status": extract_handover_status(handover_sections),
        "last_updated": extract_handover_last_updated(handover_sections),
        "updated_by": extract_handover_updated_by(handover_sections),
        "next_owner": extract_handover_next_owner(handover_sections),
        "last_completed_step": scalar_value(session_sections["Last completed step"]),
        "current_step": scalar_value(session_sections["Current step"]),
        "remaining_steps": remaining_steps,
        "what_was_done": what_was_done,
        "blockers": blockers,
        "files_touched": files_touched,
        "resume": {
            "first_file": first_file,
            "next_command": next_command,
            "prerequisites": prerequisites,
            "commands": resume_commands,
        },
        "documents": {
            "handover": str(handover_path),
            "session_state": str(session_path),
        },
        "lease": {
            "state": lease["state"],
            "holder": lease["holder"],
            "purpose": lease["purpose"],
            "acquired_at": lease["acquired_at"],
            "expires_at": lease["expires_at"],
        },
        "warnings": warnings,
    }


def build_summary_payload(handover_path: Path, session_path: Path) -> dict[str, object]:
    handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
    session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)

    warnings: list[str] = []
    warnings.extend(f"HANDOVER: {error}" for error in validate_handover_document(handover_path))
    warnings.extend(f"SESSION: {error}" for error in validate_session_document(session_path))
    warnings.extend(
        f"PAIR: {error}"
        for error in collect_pair_errors(
            handover_path=handover_path,
            session_path=session_path,
            handover_sections=handover_sections,
            session_sections=session_sections,
        )
    )
    lease = inspect_lease(start_dir=handover_path.parent.parent, explicit_root=str(handover_path.parent.parent))
    if lease["state"] == "expired":
        warnings.append(f"LEASE: Lease expired for holder {lease['holder']} at {lease['expires_at']}.")
    warnings.extend(f"LEASE: {warning}" for warning in lease["warnings"])
    warnings.extend(f"LEASE: {error}" for error in lease["errors"])

    return build_summary(
        handover_path=handover_path,
        session_path=session_path,
        handover_sections=handover_sections,
        session_sections=session_sections,
        lease=lease,
        warnings=warnings,
    )


def format_text(summary: dict[str, object]) -> str:
    resume = summary["resume"]
    lease = summary["lease"]
    lines = [
        f"Task: {summary['task']}",
        f"Status: {summary['status']}",
        f"Last updated: {summary['last_updated']}",
        f"Updated by: {summary['updated_by']}",
        f"Next owner: {summary['next_owner']}",
        f"Last completed step: {summary['last_completed_step']}",
        f"Current step: {summary['current_step']}",
        f"First file: {resume['first_file']}",
        f"Next command: {resume['next_command']}",
        f"Lease: {lease['state']}",
        f"Lease holder: {lease['holder']}",
        f"Lease expires at: {lease['expires_at']}",
        f"Handover: {summary['documents']['handover']}",
        f"Session-state: {summary['documents']['session_state']}",
    ]

    remaining_steps = summary["remaining_steps"]
    lines.append("Remaining steps:")
    if remaining_steps:
        lines.extend(f"{index}. {item}" for index, item in enumerate(remaining_steps, start=1))
    else:
        lines.append("None")

    blockers = summary["blockers"]
    lines.append("Blockers:")
    if blockers:
        lines.extend(f"- {item}" for item in blockers)
    else:
        lines.append("- None")

    what_was_done = summary["what_was_done"]
    lines.append("What was done:")
    if what_was_done:
        lines.extend(f"- {item}" for item in what_was_done)
    else:
        lines.append("- None")

    warnings = summary["warnings"]
    lines.append("Warnings:")
    if warnings:
        lines.extend(f"- {item}" for item in warnings)
    else:
        lines.append("- None")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a linked handover/session-state pair.")
    parser.add_argument("--handover", help="Path to the handover markdown file.")
    parser.add_argument("--session-state", help="Path to the session-state markdown file.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Summary output format.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when warnings are present.")
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

    summary = build_summary_payload(handover_path=handover_path, session_path=session_path)

    if args.format == "json":
        print(json.dumps(summary, indent=2))
    else:
        print(format_text(summary))

    return 1 if args.strict and summary["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
