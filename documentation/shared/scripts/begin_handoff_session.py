#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"
HANDOVER_SCRIPTS = REPO_ROOT / "documentation" / "handover" / "scripts"
SESSION_SCRIPTS = REPO_ROOT / "documentation" / "session-state" / "scripts"

for script_dir in (SHARED_SCRIPTS, HANDOVER_SCRIPTS, SESSION_SCRIPTS):
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

from generate_handover import (  # type: ignore  # noqa: E402
    build_output_path as build_handover_output_path,
    render_document as render_handover_document,
)
from generate_session_state import render_document as render_session_document  # type: ignore  # noqa: E402
from handoff_lease import (  # type: ignore  # noqa: E402
    build_lease_payload,
    inspect_lease,
    lease_path_for_docs_root,
    resolve_live_pair,
)
from reconcile_handoff_pair import (  # type: ignore  # noqa: E402
    bullet_values,
    numbered_values,
    parse_handover_blockers_and_decisions,
    parse_resume_instructions,
    parse_session_blockers,
    relative_pointer,
    render_bullets,
    render_handover_blockers_and_decisions,
    render_numbered,
    render_resume_instructions,
    render_session_blockers,
    write_markdown,
)
from report_handoff_workspace import build_workspace_report  # type: ignore  # noqa: E402
from resolve_test_docs_root import resolve_docs_root  # type: ignore  # noqa: E402
from update_handoff_pair import choose_list, choose_scalar, normalize_list  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    parse_sections as parse_handover_sections,
    validate_document as validate_handover_document,
)
from validate_handoff_pair import collect_pair_errors, parse_markdown  # type: ignore  # noqa: E402
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    extract_next_owner as extract_session_next_owner,
    extract_status as extract_session_status,
    parse_sections as parse_session_sections,
    validate_document as validate_session_document,
)


VALID_STATUSES = ("not-started", "in-progress", "blocked", "ready-for-review", "done")


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Begin active work by creating or refreshing the live pair, claiming the lease, and reporting the workspace."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--holder", required=True, help="Identifier for the human or AI starting the session.")
    parser.add_argument("--purpose", required=True, help="Short description of the work being started.")
    parser.add_argument("--task", help="Task description. Required when no live pair exists.")
    parser.add_argument("--updated-by", help="Identifier to write into the pair. Defaults to --holder.")
    parser.add_argument("--status", choices=VALID_STATUSES, help="Optional status override. Defaults to in-progress for new pairs.")
    parser.add_argument("--next-owner", help="Optional next-owner override. Defaults to the holder unless the status is done.")
    parser.add_argument(
        "--last-updated",
        default=current_timestamp(),
        help="ISO 8601 timestamp with timezone. Defaults to the current local time.",
    )
    parser.add_argument("--ttl-minutes", type=int, default=30, help="Lease duration in minutes. Defaults to 30.")
    parser.add_argument("--last-completed-step", help="Optional replacement for the last completed step.")
    parser.add_argument("--current-step", help="Optional replacement for the current step. Defaults to --purpose.")
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
    parser.add_argument("--force-lease", action="store_true", help="Replace an existing conflicting or invalid lease.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
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
        f"Lease holder: {payload['lease']['holder']}",
        f"Lease expires at: {payload['lease']['expires_at']}",
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


def validate_pair(handover_path: Path, session_path: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(f"HANDOVER: {error}" for error in validate_handover_document(handover_path))
    errors.extend(f"SESSION: {error}" for error in validate_session_document(session_path))
    if errors:
        return errors

    handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
    session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
    errors.extend(
        f"PAIR: {error}"
        for error in collect_pair_errors(
            handover_path=handover_path,
            session_path=session_path,
            handover_sections=handover_sections,
            session_sections=session_sections,
        )
    )
    return errors


def create_live_pair(args: argparse.Namespace, docs_root: Path, updated_by: str) -> tuple[Path, Path, str, str]:
    if not args.task:
        raise ValueError("No live pair exists. Pass --task to create a new live pair.")

    handover_path = build_handover_output_path(docs_root)
    session_path = docs_root / "session-state" / "CURRENT.md"
    if session_path.exists():
        raise ValueError("CURRENT.md already exists but no valid live pair could be resolved. Repair or restore it first.")

    status = args.status or "in-progress"
    next_owner = "None" if status == "done" else (args.next_owner or args.holder)
    current_step = args.current_step or args.purpose
    last_completed_step = choose_scalar(args.last_completed_step, "None")
    remaining_steps = normalize_list(args.remaining_steps)
    what_was_done = normalize_list(args.what_was_done)
    blockers = normalize_list(args.blockers)
    files_touched = normalize_list(args.files_touched)
    commands_to_resume = normalize_list(args.commands_to_resume)
    first_file = args.first_file or (files_touched[0] if files_touched else "None")
    next_command = args.next_command or (commands_to_resume[0] if commands_to_resume else "None")

    handover_pointer = relative_pointer(session_path, handover_path)
    session_pointer = relative_pointer(handover_path, session_path)

    handover_args = argparse.Namespace(
        task_summary=args.task,
        status=status,
        updated_by=updated_by,
        next_owner=next_owner,
        what_was_done=what_was_done,
        last_completed_step=last_completed_step,
        current_step=current_step,
        remaining_work=remaining_steps,
        first_file=first_file,
        next_command=next_command,
    )
    session_args = argparse.Namespace(
        task=args.task,
        status=status,
        updated_by=updated_by,
        next_owner=next_owner,
        last_completed_step=last_completed_step,
        current_step=current_step,
        remaining_steps=remaining_steps,
        blockers=blockers,
        files_touched=files_touched,
        commands_to_resume=commands_to_resume,
    )

    handover_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    handover_path.write_text(
        render_handover_document(handover_args, session_pointer, args.last_updated),
        encoding="utf-8",
    )
    session_path.write_text(
        render_session_document(session_args, handover_pointer, args.last_updated),
        encoding="utf-8",
    )

    errors = validate_pair(handover_path, session_path)
    if errors:
        raise ValueError("\n".join(errors))
    return handover_path, session_path, status, next_owner


def update_live_pair(
    args: argparse.Namespace,
    handover_path: Path,
    session_path: Path,
    updated_by: str,
) -> tuple[str, str]:
    handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
    session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)

    task = choose_scalar(args.task, handover_sections["Task summary"].strip() or session_sections["Task"].strip())
    existing_status = extract_session_status(session_sections)
    status = args.status or ("in-progress" if existing_status == "not-started" else existing_status)
    next_owner = "None" if status == "done" else (args.next_owner or args.holder)

    last_completed_step = choose_scalar(args.last_completed_step, session_sections["Last completed step"].strip())
    current_step = choose_scalar(args.current_step, args.purpose)
    remaining_steps = choose_list(
        args.remaining_steps,
        numbered_values(session_sections["Remaining steps"]) or numbered_values(handover_sections["Remaining work"]),
    )
    what_was_done = choose_list(args.what_was_done, bullet_values(handover_sections["What was done"]))
    files_touched = choose_list(args.files_touched, bullet_values(session_sections["Files touched"]))
    commands_to_resume = choose_list(args.commands_to_resume, bullet_values(session_sections["Commands to resume"]))

    current_first_file, current_next_command, current_prerequisites_text = parse_resume_instructions(
        handover_sections["Resume instructions"]
    )
    current_prerequisites = normalize_list([current_prerequisites_text]) if current_prerequisites_text != "None" else []
    first_file = choose_scalar(args.first_file, current_first_file)
    next_command = choose_scalar(args.next_command, current_next_command)
    prerequisites = choose_list(args.prerequisites, current_prerequisites)

    current_blocker, current_needed_to_unblock = parse_session_blockers(session_sections["Blockers"])
    blockers = choose_list(args.blockers, [] if current_blocker == "None" else [current_blocker])
    needed_to_unblock = current_needed_to_unblock

    _, current_decision, current_assumption = parse_handover_blockers_and_decisions(
        handover_sections["Blockers and decisions"]
    )
    decision = choose_scalar(args.decision, current_decision)
    assumption = choose_scalar(args.assumption, current_assumption)

    handover_sections["Task summary"] = task
    handover_sections["Status"] = status
    handover_sections["Last updated"] = args.last_updated
    handover_sections["Updated by"] = updated_by
    handover_sections["Next owner"] = next_owner
    handover_sections["What was done"] = render_bullets(what_was_done)
    handover_sections["Last completed step"] = last_completed_step
    handover_sections["Current step"] = current_step
    handover_sections["Remaining work"] = render_numbered(remaining_steps)
    handover_sections["Blockers and decisions"] = render_handover_blockers_and_decisions(
        "; ".join(blockers) if blockers else "None",
        decision,
        assumption,
    )
    handover_sections["Resume instructions"] = render_resume_instructions(
        first_file,
        next_command,
        "; ".join(prerequisites) if prerequisites else "None",
    )
    handover_sections["Session-state pointer"] = "None" if status == "done" else relative_pointer(handover_path, session_path)

    session_sections["Task"] = task
    session_sections["Status"] = status
    session_sections["Last updated"] = args.last_updated
    session_sections["Updated by"] = updated_by
    session_sections["Next owner"] = next_owner
    session_sections["Last completed step"] = last_completed_step
    session_sections["Current step"] = current_step
    session_sections["Remaining steps"] = render_numbered(remaining_steps)
    if blockers:
        blocker_text = blockers[0]
        if needed_to_unblock != "None":
            session_sections["Blockers"] = render_session_blockers(blocker_text, needed_to_unblock)
        else:
            session_sections["Blockers"] = render_bullets(blockers)
    else:
        session_sections["Blockers"] = "- None"
    session_sections["Decisions and assumptions"] = f"- Decision: {decision}\n- Assumption: {assumption}"
    session_sections["Files touched"] = render_bullets(files_touched)
    session_sections["Commands to resume"] = render_bullets(commands_to_resume)
    session_sections["Handover pointer"] = relative_pointer(session_path, handover_path)

    write_markdown(handover_path, HANDOVER_ROOT, list(handover_sections.keys()), handover_sections)
    write_markdown(session_path, SESSION_ROOT, list(session_sections.keys()), session_sections)

    errors = validate_pair(handover_path, session_path)
    if errors:
        raise ValueError("\n".join(errors))
    return status, next_owner


def main() -> int:
    args = parse_args()
    if args.ttl_minutes <= 0:
        payload = {
            "result": "error",
            "action": "none",
            "docs_root": "None",
            "handover": "None",
            "session_state": "None",
            "status": "None",
            "next_owner": "None",
            "lease": {"holder": args.holder, "purpose": args.purpose, "expires_at": "None"},
            "warnings": [],
            "errors": ["Lease ttl_minutes must be greater than zero."],
        }
        return emit(payload, args.format)

    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    updated_by = args.updated_by or args.holder
    existing_lease = inspect_lease(start_dir=start_dir, explicit_root=args.root)

    if existing_lease["state"] == "active" and existing_lease["holder"] != args.holder and not args.force_lease:
        payload = {
            "result": "error",
            "action": "none",
            "docs_root": str(docs_root),
            "handover": existing_lease["handover"],
            "session_state": existing_lease["session_state"],
            "status": "None",
            "next_owner": "None",
            "lease": {
                "holder": existing_lease["holder"],
                "purpose": existing_lease["purpose"],
                "expires_at": existing_lease["expires_at"],
            },
            "warnings": [],
            "errors": [f"Lease is currently held by {existing_lease['holder']}. Use --force-lease to replace it."],
        }
        return emit(payload, args.format)

    if existing_lease["state"] == "invalid" and not args.force_lease:
        payload = {
            "result": "error",
            "action": "none",
            "docs_root": str(docs_root),
            "handover": existing_lease["handover"],
            "session_state": existing_lease["session_state"],
            "status": "None",
            "next_owner": "None",
            "lease": {
                "holder": existing_lease["holder"],
                "purpose": existing_lease["purpose"],
                "expires_at": existing_lease["expires_at"],
            },
            "warnings": [],
            "errors": ["Lease is invalid. Use --force-lease to replace it."],
        }
        return emit(payload, args.format)

    action = "created"
    try:
        _, handover_path, session_path, source = resolve_live_pair(start_dir=start_dir, explicit_root=args.root)
    except ValueError:
        handover_path = None
        session_path = None
        source = "none"

    try:
        if handover_path is None or session_path is None or session_path.name != "CURRENT.md":
            handover_path, session_path, status, next_owner = create_live_pair(args, docs_root, updated_by)
            action = "created"
        else:
            status, next_owner = update_live_pair(args, handover_path, session_path, updated_by)
            action = "updated"
    except ValueError as exc:
        payload = {
            "result": "error",
            "action": action,
            "docs_root": str(docs_root),
            "handover": str(handover_path) if handover_path is not None else "None",
            "session_state": str(session_path) if session_path is not None else "None",
            "status": "None",
            "next_owner": "None",
            "lease": {"holder": args.holder, "purpose": args.purpose, "expires_at": "None"},
            "warnings": [],
            "errors": str(exc).splitlines(),
        }
        return emit(payload, args.format)

    lease_path = lease_path_for_docs_root(docs_root)
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

    report = build_workspace_report(start_dir=docs_root, explicit_root=str(docs_root), history_limit=3)
    payload = {
        "result": "ok",
        "action": action,
        "source": source,
        "docs_root": str(docs_root),
        "handover": str(handover_path),
        "session_state": str(session_path),
        "status": status,
        "next_owner": next_owner,
        "lease": {
            "holder": args.holder,
            "purpose": args.purpose,
            "expires_at": report["lease"]["expires_at"],
        },
        "warnings": report["warnings"],
        "errors": report["errors"],
        "report": report,
    }
    return emit(payload, args.format)


if __name__ == "__main__":
    raise SystemExit(main())
