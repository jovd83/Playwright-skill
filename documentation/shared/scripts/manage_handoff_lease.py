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

from handoff_lease import (  # type: ignore  # noqa: E402
    build_lease_payload,
    inspect_lease,
    lease_path_for_docs_root,
    load_lease_file,
    resolve_docs_root,
    resolve_live_pair,
)


def add_shared_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show, claim, or release the live handoff workspace lease.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser("show", help="Show the current lease state.")
    add_shared_args(show_parser)

    claim_parser = subparsers.add_parser("claim", help="Claim or refresh the live handoff workspace lease.")
    add_shared_args(claim_parser)
    claim_parser.add_argument("--holder", required=True, help="Identifier for the human or AI claiming the lease.")
    claim_parser.add_argument("--purpose", required=True, help="Short description of the work being done under the lease.")
    claim_parser.add_argument("--ttl-minutes", type=int, default=30, help="Lease duration in minutes. Defaults to 30.")
    claim_parser.add_argument("--force", action="store_true", help="Replace an existing conflicting or invalid lease.")

    release_parser = subparsers.add_parser("release", help="Release the current lease.")
    add_shared_args(release_parser)
    release_parser.add_argument("--holder", help="Identifier expected to own the lease. Required unless --force is used.")
    release_parser.add_argument("--force", action="store_true", help="Release the lease even if it belongs to another holder or is invalid.")

    return parser.parse_args()


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Docs root: {payload['docs_root']}",
        f"Lease path: {payload['lease_path']}",
        f"State: {payload['state']}",
        f"Holder: {payload['holder']}",
        f"Purpose: {payload['purpose']}",
        f"Acquired at: {payload['acquired_at']}",
        f"Expires at: {payload['expires_at']}",
        f"Handover: {payload['handover']}",
        f"Session-state: {payload['session_state']}",
        "Warnings:",
    ]
    warnings = payload["warnings"]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")
    lines.append("Errors:")
    errors = payload["errors"]
    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- None")
    return "\n".join(lines)


def emit(payload: dict[str, object], output_format: str) -> int:
    if output_format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(payload))
    return 1 if payload["errors"] else 0


def command_show(args: argparse.Namespace) -> int:
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    payload = inspect_lease(start_dir=start_dir, explicit_root=args.root)
    payload["result"] = "shown"
    return emit(payload, args.format)


def command_claim(args: argparse.Namespace) -> int:
    if args.ttl_minutes <= 0:
        payload = {
            "result": "error",
            "docs_root": "None",
            "lease_path": "None",
            "state": "invalid",
            "holder": args.holder,
            "purpose": args.purpose,
            "acquired_at": "None",
            "expires_at": "None",
            "handover": "None",
            "session_state": "None",
            "warnings": [],
            "errors": ["Lease ttl_minutes must be greater than zero."],
        }
        return emit(payload, args.format)

    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    lease_path = lease_path_for_docs_root(docs_root)
    existing = inspect_lease(start_dir=start_dir, explicit_root=args.root)

    if existing["state"] == "active" and existing["holder"] != args.holder and not args.force:
        existing = dict(existing)
        existing["result"] = "error"
        existing["errors"] = [f"Lease is currently held by {existing['holder']}. Use --force to replace it."]
        existing["warnings"] = []
        return emit(existing, args.format)

    if existing["state"] == "invalid" and not args.force:
        existing = dict(existing)
        existing["result"] = "error"
        existing["errors"] = ["Lease is invalid. Use --force to replace it."]
        existing["warnings"] = []
        return emit(existing, args.format)

    try:
        _, handover_path, session_path, source = resolve_live_pair(start_dir=start_dir, explicit_root=args.root)
    except ValueError as exc:
        payload = {
            "result": "error",
            "docs_root": str(docs_root),
            "lease_path": str(lease_path),
            "state": "invalid",
            "holder": args.holder,
            "purpose": args.purpose,
            "acquired_at": "None",
            "expires_at": "None",
            "handover": "None",
            "session_state": "None",
            "warnings": [],
            "errors": [str(exc)],
        }
        return emit(payload, args.format)

    if session_path.name != "CURRENT.md":
        payload = {
            "result": "error",
            "docs_root": str(docs_root),
            "lease_path": str(lease_path),
            "state": "invalid",
            "holder": args.holder,
            "purpose": args.purpose,
            "acquired_at": "None",
            "expires_at": "None",
            "handover": str(handover_path),
            "session_state": str(session_path),
            "warnings": [],
            "errors": ["No live CURRENT.md pair was resolved. Restore or create the live pair before claiming a lease."],
        }
        return emit(payload, args.format)

    lease_path.parent.mkdir(parents=True, exist_ok=True)
    lease_payload = build_lease_payload(
        docs_root=docs_root,
        holder=args.holder,
        purpose=args.purpose,
        handover_path=handover_path,
        session_path=session_path,
        ttl_minutes=args.ttl_minutes,
    )
    lease_path.write_text(json.dumps(lease_payload, indent=2) + "\n", encoding="utf-8")

    payload = inspect_lease(start_dir=start_dir, explicit_root=args.root)
    payload["result"] = "claimed"
    payload["source"] = source
    return emit(payload, args.format)


def command_release(args: argparse.Namespace) -> int:
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    lease_path = lease_path_for_docs_root(docs_root)
    existing = inspect_lease(start_dir=start_dir, explicit_root=args.root)

    if existing["state"] == "none":
        existing = dict(existing)
        existing["result"] = "released"
        return emit(existing, args.format)

    if not args.force and not args.holder:
        existing = dict(existing)
        existing["result"] = "error"
        existing["errors"] = ["Release requires --holder unless --force is used."]
        existing["warnings"] = []
        return emit(existing, args.format)

    if not args.force and existing["state"] == "active" and existing["holder"] != args.holder:
        existing = dict(existing)
        existing["result"] = "error"
        existing["errors"] = [f"Lease is currently held by {existing['holder']}. Use --force to release it anyway."]
        existing["warnings"] = []
        return emit(existing, args.format)

    if lease_path.exists():
        lease_path.unlink()

    payload = inspect_lease(start_dir=start_dir, explicit_root=args.root)
    payload["result"] = "released"
    return emit(payload, args.format)


def main() -> int:
    args = parse_args()
    if args.command == "show":
        return command_show(args)
    if args.command == "claim":
        return command_claim(args)
    if args.command == "release":
        return command_release(args)
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
