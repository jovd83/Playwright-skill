#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"
HANDOVER_SCRIPTS = REPO_ROOT / "documentation" / "handover" / "scripts"
SESSION_SCRIPTS = REPO_ROOT / "documentation" / "session-state" / "scripts"

for script_dir in (SHARED_SCRIPTS, HANDOVER_SCRIPTS, SESSION_SCRIPTS):
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

from resolve_latest_handoff_pair import (  # type: ignore  # noqa: E402
    HANDOVER_NAME_RE,
    resolve_latest_pair,
)
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    extract_last_updated as extract_handover_last_updated,
    extract_next_owner as extract_handover_next_owner,
    extract_pointer as extract_handover_pointer,
    extract_status as extract_handover_status,
    parse_sections as parse_handover_sections,
    resolve_pointer as resolve_handover_pointer,
    validate_document as validate_handover_document,
)
from validate_handoff_pair import collect_pair_errors, parse_markdown  # type: ignore  # noqa: E402
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    parse_sections as parse_session_sections,
    validate_document as validate_session_document,
)


def first_nonempty_line(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line:
            if line.startswith("- "):
                line = line[2:].strip()
            return line.strip("`")
    return "None"


def resolve_session_for_handover(handover_path: Path, handover_sections: dict[str, str], session_dir: Path) -> Path | None:
    pointer = extract_handover_pointer(handover_sections)
    if pointer is not None:
        linked_path = resolve_handover_pointer(handover_path, pointer)
        if linked_path.exists():
            return linked_path.resolve()

    match = HANDOVER_NAME_RE.fullmatch(handover_path.name)
    if match:
        snapshot = session_dir / f"{match.group('stamp')}_session-state.md"
        if snapshot.exists():
            return snapshot.resolve()
    return None


def sort_key(entry: dict[str, object]) -> tuple[int, str, str]:
    stamp = entry["stamp"]
    is_timestamped = 1 if stamp != "untimestamped" else 0
    return (is_timestamped, str(stamp), str(entry["handover"]))


def build_entry(handover_path: Path, session_dir: Path, active_handover: Path, active_session: Path) -> dict[str, object] | None:
    try:
        handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
    except ValueError:
        return None

    session_path = resolve_session_for_handover(handover_path, handover_sections, session_dir)
    warnings: list[str] = []
    warnings.extend(f"HANDOVER: {error}" for error in validate_handover_document(handover_path))

    session_sections = None
    if session_path is None:
        warnings.append("PAIR: No linked session-state file found for this handover.")
    else:
        warnings.extend(f"SESSION: {error}" for error in validate_session_document(session_path))
        if not any(warning.startswith("SESSION:") for warning in warnings):
            try:
                session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
            except ValueError as exc:
                warnings.append(f"SESSION: {exc}")
        if session_sections is not None:
            warnings.extend(
                f"PAIR: {error}"
                for error in collect_pair_errors(
                    handover_path=handover_path,
                    session_path=session_path,
                    handover_sections=handover_sections,
                    session_sections=session_sections,
                )
            )

    match = HANDOVER_NAME_RE.fullmatch(handover_path.name)
    stamp = match.group("stamp") if match else "untimestamped"
    kind = "live" if session_path is not None and session_path.name == "CURRENT.md" else "snapshot"
    is_active = handover_path.resolve() == active_handover.resolve() and session_path is not None and session_path.resolve() == active_session.resolve()

    return {
        "stamp": stamp,
        "task": first_nonempty_line(handover_sections["Task summary"]),
        "status": extract_handover_status(handover_sections),
        "last_updated": extract_handover_last_updated(handover_sections),
        "next_owner": extract_handover_next_owner(handover_sections),
        "handover": str(handover_path),
        "session_state": str(session_path) if session_path is not None else "None",
        "kind": kind,
        "is_active": is_active,
        "warnings": warnings,
    }


def format_text(payload: dict[str, object]) -> str:
    active = payload["active"]
    history = payload["history"]
    lines = [
        f"Docs root: {payload['docs_root']}",
        f"Active source: {payload['active_source']}",
        "Active pair:",
        f"Task: {active['task']}",
        f"Kind: {active['kind']}",
        f"Status: {active['status']}",
        f"Last updated: {active['last_updated']}",
        f"Next owner: {active['next_owner']}",
        f"Handover: {active['handover']}",
        f"Session-state: {active['session_state']}",
        "Active warnings:",
    ]
    if active["warnings"]:
        lines.extend(f"- {warning}" for warning in active["warnings"])
    else:
        lines.append("- None")

    lines.append("History:")
    if not history:
        lines.append("None")
        return "\n".join(lines)

    for index, entry in enumerate(history, start=1):
        marker = " [active]" if entry["is_active"] else ""
        lines.append(
            f"{index}. {entry['stamp']} | {entry['kind']} | {entry['status']} | {entry['next_owner']} | {entry['task']}{marker}"
        )
        lines.append(f"Handover: {entry['handover']}")
        lines.append(f"Session-state: {entry['session_state']}")
        if entry["warnings"]:
            lines.extend(f"- {warning}" for warning in entry["warnings"])
        else:
            lines.append("- Warnings: None")
    return "\n".join(lines)


def build_history_payload(start_dir: Path, limit: int | None = None) -> dict[str, object]:
    docs_root, active_handover, active_session, source = resolve_latest_pair(start_dir=start_dir)

    handover_dir = docs_root / "handovers"
    session_dir = docs_root / "session-state"
    entries: list[dict[str, object]] = []
    for handover_path in sorted(handover_dir.glob("*.md")):
        entry = build_entry(handover_path.resolve(), session_dir, active_handover, active_session)
        if entry is None:
            continue
        if active_session.name == "CURRENT.md" and entry["is_active"]:
            continue
        entries.append(entry)

    entries.sort(key=sort_key, reverse=True)
    if limit is not None:
        entries = entries[:limit]

    active_entry = build_entry(active_handover, session_dir, active_handover, active_session)
    if active_entry is None:
        raise ValueError(f"Could not parse the active handover file: {active_handover}")

    return {
        "docs_root": str(docs_root),
        "active_source": source,
        "active": active_entry,
        "history": entries,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List the active handoff pair and archived milestone history.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--limit", type=int, help="Optional maximum number of history entries to return.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        payload = build_history_payload(start_dir=Path.cwd(), limit=args.limit)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
