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

from archive_handoff_pair import derive_docs_root  # type: ignore  # noqa: E402
from reconcile_handoff_pair import relative_pointer, write_markdown  # type: ignore  # noqa: E402
from resolve_test_docs_root import resolve_docs_root  # type: ignore  # noqa: E402
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


def default_restore_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M")


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def resolve_source_pair(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    if args.timestamp:
        docs_root = resolve_docs_root(
            start_dir=Path(args.start_dir).resolve() if args.start_dir else Path.cwd(),
            explicit_root=args.root,
        )
        handover_path = docs_root / "handovers" / f"{args.timestamp}_handover.md"
        session_path = docs_root / "session-state" / f"{args.timestamp}_session-state.md"
        if not handover_path.exists():
            raise ValueError(f"Archived handover does not exist for timestamp {args.timestamp}: {handover_path}")
        if not session_path.exists():
            raise ValueError(f"Archived session-state does not exist for timestamp {args.timestamp}: {session_path}")
        return docs_root, handover_path.resolve(), session_path.resolve()

    handover_path = Path(args.handover) if args.handover else None
    session_path = Path(args.session_state) if args.session_state else None

    if handover_path is not None and not handover_path.exists():
        raise ValueError(f"Handover file does not exist: {handover_path}")
    if session_path is not None and not session_path.exists():
        raise ValueError(f"Session-state file does not exist: {session_path}")

    if handover_path is None and session_path is None:
        raise ValueError("Pass --timestamp, --handover, or --session-state to select a snapshot pair to restore.")

    if handover_path is None:
        handover_path = discover_handover_path(session_path)
    if session_path is None:
        session_path = discover_session_state_path(handover_path)

    docs_root = derive_docs_root(handover_path.resolve(), session_path.resolve())
    return docs_root, handover_path.resolve(), session_path.resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore an archived handover/session-state snapshot back into the live CURRENT.md workflow.")
    parser.add_argument("--timestamp", help="Snapshot timestamp in YYYYMMDD_HHmm format.")
    parser.add_argument("--handover", help="Path to the source handover snapshot.")
    parser.add_argument("--session-state", help="Path to the source session-state snapshot.")
    parser.add_argument("--root", help="Explicit documentation root. Used with --timestamp.")
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Used with --timestamp.")
    parser.add_argument("--updated-by", required=True, help="Identifier for the human or AI restoring the snapshot.")
    parser.add_argument("--last-updated", default=current_timestamp(), help="ISO 8601 timestamp with timezone for the restored live pair.")
    parser.add_argument("--restore-timestamp", default=default_restore_timestamp(), help="Timestamp used for the new live handover filename in YYYYMMDD_HHmm format.")
    parser.add_argument("--status", choices=VALID_STATUSES, help="Optional override for the restored status.")
    parser.add_argument("--next-owner", help="Optional override for the restored next owner.")
    parser.add_argument("--handover-output", help="Optional explicit output path for the restored live handover.")
    parser.add_argument("--session-output", help="Optional explicit output path for the restored live session-state file. Defaults to CURRENT.md.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting the target live session-state file or handover output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        docs_root, source_handover, source_session = resolve_source_pair(args)
        source_handover_sections = parse_markdown(source_handover, HANDOVER_ROOT, parse_handover_sections).copy()
        source_session_sections = parse_markdown(source_session, SESSION_ROOT, parse_session_sections).copy()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    target_handover = (
        Path(args.handover_output)
        if args.handover_output
        else docs_root / "handovers" / f"{args.restore_timestamp}_handover.md"
    )
    target_session = (
        Path(args.session_output)
        if args.session_output
        else docs_root / "session-state" / "CURRENT.md"
    )

    if target_handover.resolve() == source_handover.resolve():
        print("Restored handover output must not overwrite the source snapshot handover.", file=sys.stderr)
        return 1
    if target_session.resolve() == source_session.resolve():
        print("Restored session-state output must not overwrite the source snapshot session-state file.", file=sys.stderr)
        return 1

    protected_paths = []
    if target_session.exists():
        protected_paths.append(target_session)
    if target_handover.exists():
        protected_paths.append(target_handover)
    if protected_paths and not args.force:
        for path in protected_paths:
            print(f"Refusing to overwrite existing file: {path}", file=sys.stderr)
        return 1

    status = args.status or extract_session_status(source_session_sections) or extract_handover_status(source_handover_sections)
    next_owner = args.next_owner or extract_session_next_owner(source_session_sections) or extract_handover_next_owner(source_handover_sections)
    if status == "done":
        next_owner = "None"

    source_handover_sections["Status"] = status
    source_handover_sections["Last updated"] = args.last_updated
    source_handover_sections["Updated by"] = args.updated_by
    source_handover_sections["Next owner"] = next_owner
    source_handover_sections["Session-state pointer"] = "None" if status == "done" else relative_pointer(target_handover, target_session)

    source_session_sections["Status"] = status
    source_session_sections["Last updated"] = args.last_updated
    source_session_sections["Updated by"] = args.updated_by
    source_session_sections["Next owner"] = next_owner
    source_session_sections["Handover pointer"] = relative_pointer(target_session, target_handover)

    target_handover.parent.mkdir(parents=True, exist_ok=True)
    target_session.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(target_handover, HANDOVER_ROOT, HANDOVER_SECTIONS, source_handover_sections)
    write_markdown(target_session, SESSION_ROOT, SESSION_SECTIONS, source_session_sections)

    errors: list[str] = []
    errors.extend(f"HANDOVER: {error}" for error in validate_handover_document(target_handover))
    errors.extend(f"SESSION: {error}" for error in validate_session_document(target_session))

    if not errors:
        restored_handover_sections = parse_markdown(target_handover, HANDOVER_ROOT, parse_handover_sections)
        restored_session_sections = parse_markdown(target_session, SESSION_ROOT, parse_session_sections)
        errors.extend(
            f"PAIR: {error}"
            for error in collect_pair_errors(
                handover_path=target_handover,
                session_path=target_session,
                handover_sections=restored_handover_sections,
                session_sections=restored_session_sections,
            )
        )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Restored handoff pair: status={status}, next_owner={next_owner}")
    print(f"Source handover: {source_handover}")
    print(f"Source session-state: {source_session}")
    print(f"Handover: {target_handover}")
    print(f"Session-state: {target_session}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
