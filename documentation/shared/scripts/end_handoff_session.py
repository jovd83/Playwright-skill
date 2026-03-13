#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"

if str(SHARED_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SHARED_SCRIPTS))

from begin_handoff_session import update_live_pair  # type: ignore  # noqa: E402
from check_handoff_readiness import build_readiness_payload  # type: ignore  # noqa: E402
from handoff_lease import (  # type: ignore  # noqa: E402
    inspect_lease,
    lease_path_for_docs_root,
    resolve_docs_root,
    resolve_live_pair,
)
from report_handoff_workspace import build_workspace_report  # type: ignore  # noqa: E402


VALID_STATUSES = ("not-started", "in-progress", "blocked", "ready-for-review", "done")


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="End active work by refreshing the live pair, releasing the lease, and checking transfer readiness."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--holder", required=True, help="Identifier for the human or AI ending the session.")
    parser.add_argument("--purpose", help="Optional short description of the closure or transfer action.")
    parser.add_argument("--updated-by", help="Identifier to write into the pair. Defaults to --holder.")
    parser.add_argument("--status", choices=VALID_STATUSES, help="Optional status override.")
    parser.add_argument("--next-owner", help="Optional next-owner override.")
    parser.add_argument(
        "--last-updated",
        default=current_timestamp(),
        help="ISO 8601 timestamp with timezone. Defaults to the current local time.",
    )
    parser.add_argument("--task", help="Optional replacement for the shared task description.")
    parser.add_argument("--last-completed-step", help="Optional replacement for the last completed step.")
    parser.add_argument("--current-step", help="Optional replacement for the current step.")
    parser.add_argument("--first-file", help="Optional replacement for the first file to open.")
    parser.add_argument("--next-command", help="Optional replacement for the next command to run.")
    parser.add_argument("--decision", help="Optional replacement for the recorded decision.")
    parser.add_argument("--assumption", help="Optional replacement for the recorded assumption.")
    parser.add_argument(
        "--what-was-done",
        action="append",
        help="Repeat to replace the What was done list. Pass a single value of None to clear.",
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
        help="Repeat to replace the commands to resume list. Pass a single value of None to clear.",
    )
    parser.add_argument(
        "--prerequisite",
        dest="prerequisites",
        action="append",
        help="Repeat to replace the prerequisites list. Pass a single value of None to clear.",
    )
    parser.add_argument("--release-force", action="store_true", help="Release a conflicting or invalid lease anyway.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--strict-warnings", action="store_true", help="Return a non-zero exit code when readiness warnings remain.")
    return parser.parse_args()


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Action: {payload['action']}",
        f"Docs root: {payload['docs_root']}",
        f"Handover: {payload['handover']}",
        f"Session-state: {payload['session_state']}",
        f"Status: {payload['status']}",
        f"Next owner: {payload['next_owner']}",
        f"Readiness: {payload['readiness']['verdict']}",
        f"Lease state after release: {payload['report']['lease']['state']}",
        "Warnings:",
    ]
    if payload["warnings"]:
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    else:
        lines.append("- None")
    lines.append("Errors:")
    if payload["errors"]:
        lines.extend(f"- {error}" for error in payload["errors"])
    else:
        lines.append("- None")
    return "\n".join(lines)


def emit(payload: dict[str, object], output_format: str) -> int:
    if output_format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(payload))
    return 1 if payload["errors"] else 0


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    updated_by = args.updated_by or args.holder

    try:
        _, handover_path, session_path, source = resolve_live_pair(start_dir=start_dir, explicit_root=args.root)
    except ValueError as exc:
        payload = {
            "result": "error",
            "action": "none",
            "docs_root": str(docs_root),
            "handover": "None",
            "session_state": "None",
            "status": "None",
            "next_owner": "None",
            "readiness": {"verdict": "not-ready"},
            "warnings": [],
            "errors": [str(exc)],
        }
        return emit(payload, args.format)

    existing_lease = inspect_lease(start_dir=start_dir, explicit_root=args.root)
    if existing_lease["state"] == "active" and existing_lease["holder"] != args.holder and not args.release_force:
        payload = {
            "result": "error",
            "action": "none",
            "docs_root": str(docs_root),
            "handover": str(handover_path),
            "session_state": str(session_path),
            "status": "None",
            "next_owner": "None",
            "readiness": {"verdict": "not-ready"},
            "warnings": [],
            "errors": [f"Lease is currently held by {existing_lease['holder']}. Use --release-force to override it."],
        }
        return emit(payload, args.format)

    if existing_lease["state"] == "invalid" and not args.release_force:
        payload = {
            "result": "error",
            "action": "none",
            "docs_root": str(docs_root),
            "handover": str(handover_path),
            "session_state": str(session_path),
            "status": "None",
            "next_owner": "None",
            "readiness": {"verdict": "not-ready"},
            "warnings": [],
            "errors": ["Lease is invalid. Use --release-force to override it."],
        }
        return emit(payload, args.format)

    try:
        status, next_owner = update_live_pair(args, handover_path, session_path, updated_by)
    except ValueError as exc:
        payload = {
            "result": "error",
            "action": "updated",
            "docs_root": str(docs_root),
            "handover": str(handover_path),
            "session_state": str(session_path),
            "status": "None",
            "next_owner": "None",
            "readiness": {"verdict": "not-ready"},
            "warnings": [],
            "errors": str(exc).splitlines(),
        }
        return emit(payload, args.format)

    lease_path = lease_path_for_docs_root(docs_root)
    lease_warnings: list[str] = []
    if existing_lease["state"] == "none":
        lease_warnings.append("No active lease existed to release.")
    elif lease_path.exists():
        lease_path.unlink()
    else:
        lease_warnings.append("Lease file was already absent during release.")

    report = build_workspace_report(start_dir=docs_root, explicit_root=str(docs_root), history_limit=3)
    readiness = build_readiness_payload(report)
    warnings = [*lease_warnings, *readiness["warnings"]]
    errors: list[str] = []
    result = "ok"
    if not readiness["ready"]:
        result = "not-ready"
        errors.extend(readiness["blocking_reasons"])
    elif args.strict_warnings and readiness["warnings"]:
        result = "warning"
        errors.extend(readiness["warnings"])

    payload = {
        "result": result,
        "action": "updated-and-released",
        "source": source,
        "docs_root": str(docs_root),
        "handover": str(handover_path),
        "session_state": str(session_path),
        "status": status,
        "next_owner": next_owner,
        "readiness": readiness,
        "report": report,
        "warnings": warnings,
        "errors": errors,
    }
    return emit(payload, args.format)


if __name__ == "__main__":
    raise SystemExit(main())
