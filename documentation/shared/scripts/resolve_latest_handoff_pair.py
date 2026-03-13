#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"
HANDOVER_SCRIPTS = REPO_ROOT / "documentation" / "handover" / "scripts"
SESSION_SCRIPTS = REPO_ROOT / "documentation" / "session-state" / "scripts"

for script_dir in (SHARED_SCRIPTS, HANDOVER_SCRIPTS, SESSION_SCRIPTS):
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

from resolve_test_docs_root import resolve_docs_root  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    extract_pointer as extract_handover_pointer,
    parse_sections as parse_handover_sections,
    resolve_pointer as resolve_handover_pointer,
)
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    extract_pointer as extract_session_pointer,
    parse_sections as parse_session_sections,
    resolve_pointer as resolve_session_pointer,
)


HANDOVER_NAME_RE = re.compile(r"^(?P<stamp>\d{8}_\d{4})_handover\.md$")
SESSION_SNAPSHOT_RE = re.compile(r"^(?P<stamp>\d{8}_\d{4})_session-state\.md$")


def parse_markdown(path: Path, expected_root: str, parser) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    root_heading, sections, _ = parser(text)
    if root_heading != expected_root:
        raise ValueError(f"Unexpected root heading in {path}: {root_heading!r}")
    return sections


def candidate_sort_key(path: Path, pattern: re.Pattern[str]) -> tuple[int, str, int, str]:
    match = pattern.fullmatch(path.name)
    stamp = match.group("stamp") if match else ""
    return (1 if match else 0, stamp, path.stat().st_mtime_ns, path.name.lower())


def latest_markdown_file(directory: Path, pattern: re.Pattern[str], exclude_names: set[str] | None = None) -> Path | None:
    if not directory.exists():
        return None
    candidates = [
        path
        for path in directory.glob("*.md")
        if path.is_file() and (exclude_names is None or path.name not in exclude_names)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: candidate_sort_key(path, pattern)).resolve()


def resolve_handover_from_session(session_path: Path) -> Path | None:
    try:
        session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
    except ValueError:
        return None
    pointer = extract_session_pointer(session_sections)
    if pointer is None:
        return None
    linked_path = resolve_session_pointer(session_path, pointer)
    if linked_path.exists():
        return linked_path.resolve()
    return None


def resolve_session_from_handover(handover_path: Path) -> Path | None:
    try:
        handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
    except ValueError:
        return None
    pointer = extract_handover_pointer(handover_sections)
    if pointer is None:
        return None
    linked_path = resolve_handover_pointer(handover_path, pointer)
    if linked_path.exists():
        return linked_path.resolve()
    return None


def resolve_latest_pair(start_dir: Path | None = None, explicit_root: str | None = None) -> tuple[Path, Path, Path, str]:
    docs_root = resolve_docs_root(start_dir=start_dir or Path.cwd(), explicit_root=explicit_root)
    handover_dir = docs_root / "handovers"
    session_dir = docs_root / "session-state"

    current_session = (session_dir / "CURRENT.md").resolve()
    if current_session.exists():
        linked_handover = resolve_handover_from_session(current_session)
        if linked_handover is not None:
            return docs_root, linked_handover, current_session, "current-pointer"

    latest_handover = latest_markdown_file(handover_dir, HANDOVER_NAME_RE)
    latest_session_snapshot = latest_markdown_file(session_dir, SESSION_SNAPSHOT_RE, exclude_names={"CURRENT.md"})

    if current_session.exists() and latest_handover is not None:
        return docs_root, latest_handover, current_session, "current-plus-latest-handover"

    if latest_handover is not None:
        linked_session = resolve_session_from_handover(latest_handover)
        if linked_session is not None:
            return docs_root, latest_handover, linked_session, "latest-handover-pointer"

    if latest_handover is not None and latest_session_snapshot is not None:
        return docs_root, latest_handover, latest_session_snapshot, "latest-snapshots"

    raise ValueError(
        f"Could not resolve a handoff pair under {docs_root}. "
        "Create a linked handover/session-state pair first."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve the latest linked handover/session-state pair.")
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()

    try:
        docs_root, handover_path, session_path, source = resolve_latest_pair(start_dir=start_dir, explicit_root=args.root)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    payload = {
        "docs_root": str(docs_root),
        "handover": str(handover_path),
        "session_state": str(session_path),
        "source": source,
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"Docs root: {payload['docs_root']}")
        print(f"Handover: {payload['handover']}")
        print(f"Session-state: {payload['session_state']}")
        print(f"Source: {payload['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
