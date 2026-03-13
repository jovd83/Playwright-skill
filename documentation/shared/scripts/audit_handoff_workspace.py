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
    SESSION_SNAPSHOT_RE,
    resolve_latest_pair,
)
from handoff_lease import inspect_lease  # type: ignore  # noqa: E402
from resolve_test_docs_root import resolve_docs_root  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    parse_sections as parse_handover_sections,
    validate_document as validate_handover_document,
)
from validate_handoff_pair import collect_pair_errors, parse_markdown  # type: ignore  # noqa: E402
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    parse_sections as parse_session_sections,
    validate_document as validate_session_document,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit the full handover/session-state workspace for invalid files, broken pairs, and partial history."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


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


def format_text(payload: dict[str, object]) -> str:
    active_pair = payload["active_pair"]
    lease = payload["lease"]
    totals = payload["totals"]
    warnings = payload["warnings"]
    errors = payload["errors"]

    lines = [
        f"Docs root: {payload['docs_root']}",
        f"Result: {payload['result']}",
        "Active pair:",
    ]
    if active_pair is None:
        lines.append("- None")
    else:
        lines.append(f"- Source: {active_pair['source']}")
        lines.append(f"- Handover: {active_pair['handover']}")
        lines.append(f"- Session-state: {active_pair['session_state']}")
    lines.extend(
        [
            "Lease:",
            f"- State: {lease['state']}",
            f"- Holder: {lease['holder']}",
            f"- Purpose: {lease['purpose']}",
            f"- Expires at: {lease['expires_at']}",
        ]
    )

    lines.extend(
        [
            "Totals:",
            f"- Handover files: {totals['handover_files']}",
            f"- Session-state files: {totals['session_state_files']}",
            f"- Snapshot pairs: {totals['snapshot_pairs']}",
            f"- Orphan handovers: {totals['orphan_handovers']}",
            f"- Orphan session-state snapshots: {totals['orphan_session_snapshots']}",
            "Warnings:",
        ]
    )
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")

    lines.append("Errors:")
    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- None")

    return "\n".join(lines)


def build_audit_payload(start_dir: Path, explicit_root: str | None = None) -> dict[str, object]:
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=explicit_root)
    handover_dir = docs_root / "handovers"
    session_dir = docs_root / "session-state"
    lease = inspect_lease(start_dir=start_dir, explicit_root=explicit_root)

    handover_paths = sorted(path.resolve() for path in handover_dir.glob("*.md") if path.is_file()) if handover_dir.exists() else []
    session_paths = sorted(path.resolve() for path in session_dir.glob("*.md") if path.is_file()) if session_dir.exists() else []

    errors: list[str] = []
    warnings: list[str] = []
    valid_handover_paths: set[Path] = set()
    valid_session_paths: set[Path] = set()

    if not handover_paths and not session_paths:
        errors.append("No handover or session-state markdown files were found under the documentation root.")

    for handover_path in handover_paths:
        handover_errors = validate_handover_document(handover_path)
        if handover_errors:
            errors.extend(f"{handover_path.name}: {error}" for error in handover_errors)
        else:
            valid_handover_paths.add(handover_path)

    for session_path in session_paths:
        session_errors = validate_session_document(session_path)
        if session_errors:
            errors.extend(f"{session_path.name}: {error}" for error in session_errors)
        else:
            valid_session_paths.add(session_path)

    active_pair: dict[str, str] | None = None
    pair_candidates: dict[tuple[str, str], tuple[Path, Path]] = {}
    try:
        _, active_handover_path, active_session_path, active_source = resolve_latest_pair(
            start_dir=start_dir,
            explicit_root=explicit_root,
        )
    except ValueError as exc:
        warnings.append(f"Active pair could not be resolved: {exc}")
    else:
        active_pair = {
            "source": active_source,
            "handover": str(active_handover_path),
            "session_state": str(active_session_path),
        }
        pair_candidates[(str(active_handover_path), str(active_session_path))] = (
            active_handover_path,
            active_session_path,
        )

    handover_snapshots: dict[str, Path] = {}
    session_snapshots: dict[str, Path] = {}
    for handover_path in handover_paths:
        stamp = timestamp_for_handover(handover_path)
        if stamp is not None:
            handover_snapshots[stamp] = handover_path
    for session_path in session_paths:
        stamp = timestamp_for_session(session_path)
        if stamp is not None:
            session_snapshots[stamp] = session_path

    if active_pair is not None and active_pair["session_state"].endswith("CURRENT.md"):
        active_handover_stamp = timestamp_for_handover(Path(active_pair["handover"]))
        if active_handover_stamp is not None:
            handover_snapshots.pop(active_handover_stamp, None)

    common_stamps = sorted(set(handover_snapshots) & set(session_snapshots))
    for stamp in common_stamps:
        handover_path = handover_snapshots[stamp]
        session_path = session_snapshots[stamp]
        pair_candidates[(str(handover_path), str(session_path))] = (handover_path, session_path)

    for stamp in sorted(set(handover_snapshots) - set(session_snapshots)):
        warnings.append(
            f"Snapshot handover has no timestamp-matched session-state snapshot: {handover_snapshots[stamp].name}"
        )
    for stamp in sorted(set(session_snapshots) - set(handover_snapshots)):
        warnings.append(
            f"Snapshot session-state has no timestamp-matched handover snapshot: {session_snapshots[stamp].name}"
        )

    if lease["state"] == "expired":
        warnings.append(
            f"Lease expired for holder {lease['holder']} at {lease['expires_at']}."
        )
    warnings.extend(f"Lease: {warning}" for warning in lease["warnings"])
    errors.extend(f"Lease: {error}" for error in lease["errors"])

    for handover_path, session_path in pair_candidates.values():
        if handover_path not in valid_handover_paths or session_path not in valid_session_paths:
            continue
        try:
            handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
            session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        pair_errors = collect_pair_errors(
            handover_path=handover_path,
            session_path=session_path,
            handover_sections=handover_sections,
            session_sections=session_sections,
        )
        errors.extend(
            f"{handover_path.name} <-> {session_path.name}: {pair_error}"
            for pair_error in pair_errors
        )

    result = "clean"
    if errors:
        result = "error"
    elif warnings:
        result = "warning"

    payload = {
        "docs_root": str(docs_root),
        "result": result,
        "active_pair": active_pair,
        "lease": {
            "state": lease["state"],
            "holder": lease["holder"],
            "purpose": lease["purpose"],
            "acquired_at": lease["acquired_at"],
            "expires_at": lease["expires_at"],
            "handover": lease["handover"],
            "session_state": lease["session_state"],
        },
        "totals": {
            "handover_files": len(handover_paths),
            "session_state_files": len(session_paths),
            "snapshot_pairs": len(common_stamps),
            "orphan_handovers": len(set(handover_snapshots) - set(session_snapshots)),
            "orphan_session_snapshots": len(set(session_snapshots) - set(handover_snapshots)),
        },
        "warnings": warnings,
        "errors": errors,
    }
    return payload


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    payload = build_audit_payload(start_dir=start_dir, explicit_root=args.root)

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(payload))
    return 1 if payload["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
