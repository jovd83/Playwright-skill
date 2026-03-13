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

from report_handoff_workspace import build_workspace_report  # type: ignore  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether the active handoff workspace is ready to transfer to the next operator."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--history-limit", type=int, default=3, help="Maximum number of history entries to include in the embedded report. Defaults to 3.")
    parser.add_argument("--strict-warnings", action="store_true", help="Return a non-zero exit code when warnings are present.")
    return parser.parse_args()


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def build_readiness_payload(report: dict[str, object]) -> dict[str, object]:
    summary = report["summary"]
    lease = report["lease"]
    audit = report["audit"]

    blocking_reasons: list[str] = []
    warnings = list(report["warnings"])
    next_actions: list[str] = []

    if report["errors"]:
        blocking_reasons.extend(report["errors"])
        next_actions.append("Run python ../shared/scripts/repair_handoff_workspace.py --updated-by <actor> --format text.")
        next_actions.append("Re-run python ../shared/scripts/validate_handoff_pair.py after the repair.")

    if lease["state"] == "active":
        blocking_reasons.append(
            f"Live lease is still active for holder {lease['holder']}. Release it before transfer."
        )
        next_actions.append(
            f"Run python ../shared/scripts/manage_handoff_lease.py release --holder {lease['holder']} --format text."
        )
    elif lease["state"] == "expired":
        blocking_reasons.append(
            f"Live lease expired for holder {lease['holder']} at {lease['expires_at']}."
        )
        next_actions.append("Run python ../shared/scripts/manage_handoff_lease.py show --format text.")
        next_actions.append(
            "Replace the stale lease with claim --force only after confirming the previous holder is no longer editing."
        )
    elif lease["state"] == "invalid":
        blocking_reasons.append("Live lease is invalid or points to missing files.")
        next_actions.append("Run python ../shared/scripts/manage_handoff_lease.py show --format text.")

    if not blocking_reasons and warnings:
        next_actions.append("Review the warning list in python ../shared/scripts/report_handoff_workspace.py --format text.")

    blocking_reasons = dedupe(blocking_reasons)
    warnings = dedupe(warnings)
    next_actions = dedupe(next_actions)

    verdict = "ready"
    ready = True
    if blocking_reasons:
        verdict = "not-ready"
        ready = False
    elif warnings:
        verdict = "ready-with-warnings"

    return {
        "docs_root": report["docs_root"],
        "verdict": verdict,
        "ready": ready,
        "task": summary["task"],
        "status": summary["status"],
        "next_owner": summary["next_owner"],
        "lease": lease,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "next_actions": next_actions,
        "report": report,
    }


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Verdict: {payload['verdict']}",
        f"Ready: {payload['ready']}",
        f"Docs root: {payload['docs_root']}",
        f"Task: {payload['task']}",
        f"Status: {payload['status']}",
        f"Next owner: {payload['next_owner']}",
        f"Lease state: {payload['lease']['state']}",
        f"Lease holder: {payload['lease']['holder']}",
        "Blocking reasons:",
    ]
    if payload["blocking_reasons"]:
        lines.extend(f"- {reason}" for reason in payload["blocking_reasons"])
    else:
        lines.append("- None")

    lines.append("Warnings:")
    if payload["warnings"]:
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    else:
        lines.append("- None")

    lines.append("Next actions:")
    if payload["next_actions"]:
        lines.extend(f"{index}. {action}" for index, action in enumerate(payload["next_actions"], start=1))
    else:
        lines.append("1. None")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()

    try:
        report = build_workspace_report(start_dir=start_dir, explicit_root=args.root, history_limit=args.history_limit)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    payload = build_readiness_payload(report)

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(payload))

    if not payload["ready"]:
        return 1
    if args.strict_warnings and payload["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
