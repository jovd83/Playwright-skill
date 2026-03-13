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

from reconcile_handoff_pair import relative_pointer, write_markdown  # type: ignore  # noqa: E402
from resolve_latest_handoff_pair import resolve_latest_pair  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    REQUIRED_SECTIONS as HANDOVER_SECTIONS,
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
    parse_sections as parse_session_sections,
    validate_document as validate_session_document,
)


def default_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M")


def derive_docs_root(handover_path: Path, session_path: Path) -> Path:
    if handover_path.parent.name == "handovers" and session_path.parent.name == "session-state":
        if handover_path.parent.parent == session_path.parent.parent:
            return handover_path.parent.parent
    if handover_path.parent.name == "handovers":
        return handover_path.parent.parent
    if session_path.parent.name == "session-state":
        return session_path.parent.parent
    raise ValueError("Could not derive the shared documentation root from the provided pair.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive a linked handover/session-state pair into timestamped snapshots.")
    parser.add_argument("--handover", help="Path to the handover markdown file.")
    parser.add_argument("--session-state", help="Path to the session-state markdown file.")
    parser.add_argument("--timestamp", default=default_timestamp(), help="Archive timestamp in YYYYMMDD_HHmm format.")
    parser.add_argument("--handover-output", help="Optional explicit archive path for the handover snapshot.")
    parser.add_argument("--session-output", help="Optional explicit archive path for the session-state snapshot.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing snapshot files if they already exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if not args.handover and not args.session_state:
            docs_root, handover_path, session_path, _ = resolve_latest_pair(start_dir=Path.cwd())
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

            docs_root = derive_docs_root(handover_path, session_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    archive_handover_path = (
        Path(args.handover_output)
        if args.handover_output
        else docs_root / "handovers" / f"{args.timestamp}_handover.md"
    )
    archive_session_path = (
        Path(args.session_output)
        if args.session_output
        else docs_root / "session-state" / f"{args.timestamp}_session-state.md"
    )

    if archive_handover_path.resolve() == handover_path.resolve():
        print("Archive handover output must not overwrite the source handover file.", file=sys.stderr)
        return 1
    if archive_session_path.resolve() == session_path.resolve():
        print("Archive session-state output must not overwrite the source session-state file.", file=sys.stderr)
        return 1

    for path in (archive_handover_path, archive_session_path):
        if path.exists() and not args.force:
            print(f"Refusing to overwrite existing file: {path}", file=sys.stderr)
            return 1

    try:
        handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections).copy()
        session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections).copy()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    handover_sections["Session-state pointer"] = relative_pointer(archive_handover_path, archive_session_path)
    session_sections["Handover pointer"] = relative_pointer(archive_session_path, archive_handover_path)

    archive_handover_path.parent.mkdir(parents=True, exist_ok=True)
    archive_session_path.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(archive_handover_path, HANDOVER_ROOT, HANDOVER_SECTIONS, handover_sections)
    write_markdown(archive_session_path, SESSION_ROOT, SESSION_SECTIONS, session_sections)

    errors: list[str] = []
    errors.extend(f"HANDOVER: {error}" for error in validate_handover_document(archive_handover_path))
    errors.extend(f"SESSION: {error}" for error in validate_session_document(archive_session_path))

    if not errors:
        archived_handover_sections = parse_markdown(archive_handover_path, HANDOVER_ROOT, parse_handover_sections)
        archived_session_sections = parse_markdown(archive_session_path, SESSION_ROOT, parse_session_sections)
        errors.extend(
            f"PAIR: {error}"
            for error in collect_pair_errors(
                handover_path=archive_handover_path,
                session_path=archive_session_path,
                handover_sections=archived_handover_sections,
                session_sections=archived_session_sections,
            )
        )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Archived handoff pair: timestamp={args.timestamp}")
    print(f"Handover: {archive_handover_path}")
    print(f"Session-state: {archive_session_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
