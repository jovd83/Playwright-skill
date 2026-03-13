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

from audit_handoff_workspace import build_audit_payload  # type: ignore  # noqa: E402
from reconcile_handoff_pair import relative_pointer, reconcile_pair  # type: ignore  # noqa: E402
from resolve_latest_handoff_pair import (  # type: ignore  # noqa: E402
    HANDOVER_NAME_RE,
    SESSION_SNAPSHOT_RE,
    resolve_latest_pair,
)
from resolve_test_docs_root import resolve_docs_root  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    REQUIRED_SECTIONS as HANDOVER_SECTIONS,
    extract_pointer as extract_handover_pointer,
    parse_sections as parse_handover_sections,
    resolve_pointer as resolve_handover_pointer,
    validate_document as validate_handover_document,
)
from validate_handoff_pair import collect_pair_errors, parse_markdown  # type: ignore  # noqa: E402
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    REQUIRED_SECTIONS as SESSION_SECTIONS,
    extract_pointer as extract_session_pointer,
    parse_sections as parse_session_sections,
    resolve_pointer as resolve_session_pointer,
    validate_document as validate_session_document,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Repair the live handoff pair and safe archived snapshot cross-links within the documentation workspace."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--updated-by", required=True, help="Identifier for the human or AI performing the repair.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def render_markdown(root_heading: str, ordered_sections: list[str], sections: dict[str, str]) -> str:
    parts = [root_heading, ""]
    for section in ordered_sections:
        parts.append(f"## {section}")
        parts.append(sections[section].rstrip())
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def timestamp_for_handover(path: Path) -> str | None:
    match = HANDOVER_NAME_RE.fullmatch(path.name)
    if match is None:
        return None
    return match.group("stamp")


def timestamp_for_session(path: Path) -> str | None:
    match = SESSION_SNAPSHOT_RE.fullmatch(path.name)
    if match is None:
        return None
    return match.group("stamp")


def resolve_live_pair_for_repair(start_dir: Path, explicit_root: str | None) -> tuple[Path, Path, str]:
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=explicit_root)
    current_session = (docs_root / "session-state" / "CURRENT.md").resolve()
    handover_dir = docs_root / "handovers"

    if current_session.exists():
        try:
            session_root, session_sections, _ = parse_session_sections(current_session.read_text(encoding="utf-8"))
            if session_root == SESSION_ROOT:
                pointer = extract_session_pointer(session_sections)
                if pointer is not None:
                    linked_handover = resolve_session_pointer(current_session, pointer)
                    if linked_handover.exists():
                        return linked_handover.resolve(), current_session, "current-pointer"
        except Exception:
            pass

        for handover_path in sorted(handover_dir.glob("*.md")):
            handover_path = handover_path.resolve()
            try:
                handover_root, handover_sections, _ = parse_handover_sections(handover_path.read_text(encoding="utf-8"))
                if handover_root != HANDOVER_ROOT:
                    continue
                pointer = extract_handover_pointer(handover_sections)
                if pointer is None:
                    continue
                linked_session = resolve_handover_pointer(handover_path, pointer)
                if linked_session.resolve() == current_session:
                    return handover_path, current_session, "back-pointer-scan"
            except Exception:
                continue

        non_timestamped = [
            path.resolve()
            for path in sorted(handover_dir.glob("*.md"))
            if HANDOVER_NAME_RE.fullmatch(path.name) is None
        ]
        if len(non_timestamped) == 1:
            return non_timestamped[0], current_session, "current-plus-single-live-handover"

    _, handover_path, session_path, source = resolve_latest_pair(start_dir=start_dir, explicit_root=explicit_root)
    return handover_path, session_path, source


def repair_snapshot_pair(handover_path: Path, session_path: Path) -> tuple[bool, list[str]]:
    original_handover = handover_path.read_text(encoding="utf-8")
    original_session = session_path.read_text(encoding="utf-8")

    try:
        handover_root, handover_sections, _ = parse_handover_sections(original_handover)
        session_root, session_sections, _ = parse_session_sections(original_session)
        if handover_root != HANDOVER_ROOT:
            return False, [f"{handover_path.name}: unexpected root heading {handover_root!r}."]
        if session_root != SESSION_ROOT:
            return False, [f"{session_path.name}: unexpected root heading {session_root!r}."]

        for section in HANDOVER_SECTIONS:
            if section not in handover_sections:
                return False, [f"{handover_path.name}: missing required section {section!r}; snapshot repair skipped."]
        for section in SESSION_SECTIONS:
            if section not in session_sections:
                return False, [f"{session_path.name}: missing required section {section!r}; snapshot repair skipped."]

        handover_sections = handover_sections.copy()
        session_sections = session_sections.copy()
        handover_sections["Session-state pointer"] = relative_pointer(handover_path, session_path)
        session_sections["Handover pointer"] = relative_pointer(session_path, handover_path)

        new_handover = render_markdown(HANDOVER_ROOT, HANDOVER_SECTIONS, handover_sections)
        new_session = render_markdown(SESSION_ROOT, SESSION_SECTIONS, session_sections)
        if new_handover == original_handover and new_session == original_session:
            return False, []

        handover_path.write_text(new_handover, encoding="utf-8")
        session_path.write_text(new_session, encoding="utf-8")

        errors: list[str] = []
        errors.extend(f"{handover_path.name}: {error}" for error in validate_handover_document(handover_path))
        errors.extend(f"{session_path.name}: {error}" for error in validate_session_document(session_path))
        if not errors:
            handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
            session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
            errors.extend(
                f"{handover_path.name} <-> {session_path.name}: {error}"
                for error in collect_pair_errors(
                    handover_path=handover_path,
                    session_path=session_path,
                    handover_sections=handover_sections,
                    session_sections=session_sections,
                )
            )
        if errors:
            handover_path.write_text(original_handover, encoding="utf-8")
            session_path.write_text(original_session, encoding="utf-8")
            return False, errors

        return True, []
    except Exception as exc:
        handover_path.write_text(original_handover, encoding="utf-8")
        session_path.write_text(original_session, encoding="utf-8")
        return False, [f"{handover_path.name} <-> {session_path.name}: snapshot repair failed: {exc}"]


def format_text(payload: dict[str, object]) -> str:
    active = payload["active_pair"]
    repairs = payload["repairs"]
    audit = payload["audit"]
    lines = [
        f"Docs root: {payload['docs_root']}",
        f"Result: {payload['result']}",
        "Active pair repair:",
    ]
    if active is None:
        lines.append("- Skipped")
    else:
        changed = "changed" if active["changed"] else "no changes"
        lines.append(f"- Source: {active['source']}")
        lines.append(f"- Status: {active['status']}")
        lines.append(f"- Next owner: {active['next_owner']}")
        lines.append(f"- Outcome: {changed}")

    lines.append("Snapshot repairs:")
    if repairs["snapshot_pairs_repaired"]:
        lines.extend(f"- {stamp}" for stamp in repairs["snapshot_pairs_repaired"])
    else:
        lines.append("- None")

    lines.append("Repair notes:")
    if repairs["notes"]:
        lines.extend(f"- {note}" for note in repairs["notes"])
    else:
        lines.append("- None")

    lines.append("Audit warnings:")
    if audit["warnings"]:
        lines.extend(f"- {warning}" for warning in audit["warnings"])
    else:
        lines.append("- None")

    lines.append("Audit errors:")
    if audit["errors"]:
        lines.extend(f"- {error}" for error in audit["errors"])
    else:
        lines.append("- None")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    handover_dir = docs_root / "handovers"
    session_dir = docs_root / "session-state"

    notes: list[str] = []
    repaired_snapshot_pairs: list[str] = []
    active_pair_payload: dict[str, object] | None = None

    try:
        active_handover_path, active_session_path, active_source = resolve_live_pair_for_repair(
            start_dir=start_dir,
            explicit_root=args.root,
        )
    except ValueError as exc:
        notes.append(f"Active pair could not be resolved for repair: {exc}")
    else:
        if active_session_path.name == "CURRENT.md":
            before_handover = active_handover_path.read_text(encoding="utf-8")
            before_session = active_session_path.read_text(encoding="utf-8")
            try:
                status, next_owner = reconcile_pair(
                    handover_path=active_handover_path,
                    session_path=active_session_path,
                    updated_by=args.updated_by,
                    explicit_next_owner=None,
                    explicit_status=None,
                )
                after_handover = active_handover_path.read_text(encoding="utf-8")
                after_session = active_session_path.read_text(encoding="utf-8")
                active_pair_payload = {
                    "source": active_source,
                    "handover": str(active_handover_path),
                    "session_state": str(active_session_path),
                    "status": status,
                    "next_owner": next_owner,
                    "changed": before_handover != after_handover or before_session != after_session,
                }
            except ValueError as exc:
                notes.append(f"Active pair repair failed: {exc}")
        else:
            notes.append("No live CURRENT.md pair was resolved; active pair reconciliation was skipped.")

    handover_snapshots: dict[str, Path] = {}
    session_snapshots: dict[str, Path] = {}
    if handover_dir.exists():
        for handover_path in sorted(path.resolve() for path in handover_dir.glob("*.md") if path.is_file()):
            stamp = timestamp_for_handover(handover_path)
            if stamp is not None:
                handover_snapshots[stamp] = handover_path
    if session_dir.exists():
        for session_path in sorted(path.resolve() for path in session_dir.glob("*.md") if path.is_file()):
            stamp = timestamp_for_session(session_path)
            if stamp is not None:
                session_snapshots[stamp] = session_path

    for stamp in sorted(set(handover_snapshots) & set(session_snapshots)):
        changed, snapshot_notes = repair_snapshot_pair(
            handover_path=handover_snapshots[stamp],
            session_path=session_snapshots[stamp],
        )
        if changed:
            repaired_snapshot_pairs.append(stamp)
        notes.extend(snapshot_notes)

    audit_payload = build_audit_payload(start_dir=start_dir, explicit_root=args.root)
    payload = {
        "docs_root": str(docs_root),
        "result": audit_payload["result"],
        "active_pair": active_pair_payload,
        "repairs": {
            "snapshot_pairs_repaired": repaired_snapshot_pairs,
            "notes": notes,
        },
        "audit": audit_payload,
    }

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(payload))
    return 1 if audit_payload["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
