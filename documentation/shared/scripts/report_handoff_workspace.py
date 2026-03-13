#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"

if str(SHARED_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SHARED_SCRIPTS))

from audit_handoff_workspace import build_audit_payload  # type: ignore  # noqa: E402
from handoff_lease import inspect_lease, resolve_live_pair  # type: ignore  # noqa: E402
from list_handoff_history import build_history_payload  # type: ignore  # noqa: E402
from summarize_handoff_pair import build_summary_payload  # type: ignore  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report the active handoff workspace state, including lease, health, resume details, and recent history."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--history-limit", type=int, default=3, help="Maximum number of history entries to include. Defaults to 3.")
    return parser.parse_args()


def format_text(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    audit = payload["audit"]
    history = payload["history"]["history"]
    lease = payload["lease"]

    lines = [
        f"Docs root: {payload['docs_root']}",
        f"Result: {payload['result']}",
        f"Task: {summary['task']}",
        f"Status: {summary['status']}",
        f"Last updated: {summary['last_updated']}",
        f"Updated by: {summary['updated_by']}",
        f"Next owner: {summary['next_owner']}",
        f"Current step: {summary['current_step']}",
        f"Next command: {summary['resume']['next_command']}",
        f"Handover: {summary['documents']['handover']}",
        f"Session-state: {summary['documents']['session_state']}",
        "Lease:",
        f"- State: {lease['state']}",
        f"- Holder: {lease['holder']}",
        f"- Purpose: {lease['purpose']}",
        f"- Expires at: {lease['expires_at']}",
        "Workspace health:",
        f"- Audit result: {audit['result']}",
        f"- Warning count: {len(audit['warnings'])}",
        f"- Error count: {len(audit['errors'])}",
        "Remaining steps:",
    ]

    if summary["remaining_steps"]:
        lines.extend(f"{index}. {step}" for index, step in enumerate(summary["remaining_steps"], start=1))
    else:
        lines.append("None")

    lines.append("Recent history:")
    if history:
        for index, entry in enumerate(history, start=1):
            lines.append(
                f"{index}. {entry['stamp']} | {entry['kind']} | {entry['status']} | {entry['next_owner']} | {entry['task']}"
            )
    else:
        lines.append("None")

    lines.append("Warnings:")
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


def build_workspace_report(start_dir: Path, explicit_root: str | None = None, history_limit: int = 3) -> dict[str, object]:
    docs_root, handover_path, session_path, _ = resolve_live_pair(start_dir=start_dir, explicit_root=explicit_root)
    summary = build_summary_payload(handover_path=handover_path, session_path=session_path)
    audit = build_audit_payload(start_dir=start_dir, explicit_root=explicit_root)
    history = build_history_payload(start_dir=start_dir, limit=history_limit)
    lease = inspect_lease(start_dir=start_dir, explicit_root=explicit_root)

    warnings = [*summary["warnings"], *audit["warnings"]]
    errors = list(audit["errors"])
    result = "clean"
    if errors:
        result = "error"
    elif warnings:
        result = "warning"

    return {
        "docs_root": str(docs_root),
        "result": result,
        "summary": summary,
        "lease": {
            "state": lease["state"],
            "holder": lease["holder"],
            "purpose": lease["purpose"],
            "acquired_at": lease["acquired_at"],
            "expires_at": lease["expires_at"],
        },
        "audit": audit,
        "history": history,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()

    try:
        payload = build_workspace_report(start_dir=start_dir, explicit_root=args.root, history_limit=args.history_limit)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(payload))
    return 1 if payload["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
