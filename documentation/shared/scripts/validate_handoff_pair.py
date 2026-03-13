#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
    extract_last_updated as extract_session_last_updated,
    extract_next_owner as extract_session_next_owner,
    extract_pointer as extract_session_pointer,
    extract_status as extract_session_status,
    extract_updated_by as extract_session_updated_by,
    parse_sections as parse_session_sections,
    resolve_pointer as resolve_session_pointer,
    validate_document as validate_session_document,
)


def parse_markdown(path: Path, expected_root: str, parser) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    root_heading, sections, _ = parser(text)
    if root_heading != expected_root:
        raise ValueError(f"Unexpected root heading in {path}: {root_heading!r}")
    return sections


def relative_pointer(from_path: Path, to_path: Path) -> str:
    return Path(os.path.relpath(to_path.resolve(), start=from_path.resolve().parent)).as_posix()


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


def allow_missing_pointer(status: str) -> bool:
    return status == "done"


def collect_pair_errors(
    handover_path: Path,
    session_path: Path,
    handover_sections: dict[str, str],
    session_sections: dict[str, str],
) -> list[str]:
    errors: list[str] = []

    handover_status = extract_handover_status(handover_sections)
    session_status = extract_session_status(session_sections)
    if handover_status != session_status:
        errors.append(f"Status mismatch between handover ({handover_status}) and session-state ({session_status}).")

    handover_updated_by = extract_handover_updated_by(handover_sections)
    session_updated_by = extract_session_updated_by(session_sections)
    if handover_updated_by != session_updated_by:
        errors.append(
            f"Updated by mismatch between handover ({handover_updated_by}) and session-state ({session_updated_by})."
        )

    handover_next_owner = extract_handover_next_owner(handover_sections)
    session_next_owner = extract_session_next_owner(session_sections)
    if handover_next_owner != session_next_owner:
        errors.append(
            f"Next owner mismatch between handover ({handover_next_owner}) and session-state ({session_next_owner})."
        )

    handover_last_updated = extract_handover_last_updated(handover_sections)
    session_last_updated = extract_session_last_updated(session_sections)
    if handover_last_updated != session_last_updated:
        errors.append(
            "Last updated mismatch between handover "
            f"({handover_last_updated}) and session-state ({session_last_updated})."
        )

    expected_session_pointer = relative_pointer(handover_path, session_path)
    actual_session_pointer = extract_handover_pointer(handover_sections)
    if actual_session_pointer is None:
        if not allow_missing_pointer(handover_status):
            errors.append("Handover is missing the linked session-state pointer.")
    elif actual_session_pointer != expected_session_pointer:
        errors.append(
            f"Session-state pointer mismatch: expected {expected_session_pointer!r}, found {actual_session_pointer!r}."
        )

    expected_handover_pointer = relative_pointer(session_path, handover_path)
    actual_handover_pointer = extract_session_pointer(session_sections)
    if actual_handover_pointer is None:
        if not allow_missing_pointer(session_status):
            errors.append("Session-state is missing the linked handover pointer.")
    elif actual_handover_pointer != expected_handover_pointer:
        errors.append(
            f"Handover pointer mismatch: expected {expected_handover_pointer!r}, found {actual_handover_pointer!r}."
        )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a linked handover and session-state pair.")
    parser.add_argument("--handover", help="Path to the handover markdown file.")
    parser.add_argument("--session-state", help="Path to the session-state markdown file.")
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

    handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
    session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
    print(
        "Valid handoff pair: "
        f"status={extract_handover_status(handover_sections)}, "
        f"next_owner={extract_handover_next_owner(handover_sections)}"
    )
    print(f"Handover: {handover_path}")
    print(f"Session-state: {session_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
