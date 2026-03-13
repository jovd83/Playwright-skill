#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"
HANDOVER_SCRIPTS = REPO_ROOT / "documentation" / "handover" / "scripts"
SESSION_SCRIPTS = REPO_ROOT / "documentation" / "session-state" / "scripts"

for script_dir in (SHARED_SCRIPTS, HANDOVER_SCRIPTS, SESSION_SCRIPTS):
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

from handoff_lease import lease_path_for_docs_root, validate_lease_payload  # type: ignore  # noqa: E402
from handoff_bundle import (  # type: ignore  # noqa: E402
    BUNDLE_VERSION,
    load_bundle,
    require_mapping,
    require_string,
    validate_bundle_documents,
)
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    extract_last_updated as extract_handover_last_updated,
    extract_next_owner as extract_handover_next_owner,
    extract_status as extract_handover_status,
    extract_updated_by as extract_handover_updated_by,
    parse_sections as parse_handover_sections,
    validate_document as validate_handover_document,
)
from validate_handoff_pair import collect_pair_errors, parse_markdown  # type: ignore  # noqa: E402
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    extract_next_owner as extract_session_next_owner,
    parse_sections as parse_session_sections,
    validate_document as validate_session_document,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a portable handoff bundle before import and validate its embedded pair, lease payload, and captured source state."
    )
    parser.add_argument("--bundle", required=True, help="Path to the exported handoff bundle JSON file.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when warnings are present.")
    return parser.parse_args()


def normalize_line(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("`") and stripped.endswith("`") and len(stripped) >= 2:
        return stripped[1:-1]
    return stripped


def scalar_value(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        return normalize_line(line)
    return "None"


def stage_bundle_documents(
    bundle: dict[str, object],
    docs_root: Path,
) -> tuple[Path, Path]:
    source = require_mapping(bundle["source"], "Bundle source")
    documents = require_mapping(bundle["documents"], "Bundle documents")

    handover_path = docs_root / "handovers" / require_string(source.get("handover_name"), "Bundle source handover_name")
    session_path = docs_root / "session-state" / require_string(
        source.get("session_state_name"), "Bundle source session_state_name"
    )
    handover_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    handover_path.write_text(require_string(documents.get("handover_markdown"), "Bundle handover_markdown"), encoding="utf-8")
    session_path.write_text(
        require_string(documents.get("session_state_markdown"), "Bundle session_state_markdown"),
        encoding="utf-8",
    )
    return handover_path, session_path


def build_bundle_payload(bundle_path: Path) -> dict[str, object]:
    bundle = load_bundle(bundle_path)
    handover_sections, session_sections = validate_bundle_documents(bundle)
    source = require_mapping(bundle["source"], "Bundle source")
    report = require_mapping(bundle.get("report"), "Bundle report")
    readiness = require_mapping(bundle.get("readiness"), "Bundle readiness")
    lease = require_mapping(bundle.get("lease"), "Bundle lease")
    signature = bundle.get("signature") if isinstance(bundle.get("signature"), dict) else {}
    git = bundle.get("git") if isinstance(bundle.get("git"), dict) else {}
    redaction = bundle.get("redaction") if isinstance(bundle.get("redaction"), dict) else {}

    task = scalar_value(handover_sections["Task summary"])
    status = extract_handover_status(handover_sections)
    updated_by = extract_handover_updated_by(handover_sections)
    last_updated = extract_handover_last_updated(handover_sections)
    next_owner = extract_handover_next_owner(handover_sections)

    warnings: list[str] = []
    errors: list[str] = []

    source_handover = require_string(source.get("handover"), "Bundle source handover")
    source_session = require_string(source.get("session_state"), "Bundle source session_state")
    handover_name = require_string(source.get("handover_name"), "Bundle source handover_name")
    session_name = require_string(source.get("session_state_name"), "Bundle source session_state_name")

    if Path(source_handover).name != handover_name:
        errors.append("Bundle source handover path does not match source handover_name.")
    if Path(source_session).name != session_name:
        errors.append("Bundle source session-state path does not match source session_state_name.")
    if extract_session_next_owner(session_sections) != next_owner:
        errors.append("Bundle embedded handover and session-state files disagree on Next owner.")

    report_summary = require_mapping(report.get("summary"), "Bundle report summary")
    if str(report_summary.get("task", "")) != task:
        errors.append("Bundle report summary task does not match the embedded handover task.")
    if str(report_summary.get("status", "")) != status:
        errors.append("Bundle report summary status does not match the embedded handover status.")
    if str(report_summary.get("next_owner", "")) != next_owner:
        errors.append("Bundle report summary next owner does not match the embedded handover next owner.")

    readiness_task = str(readiness.get("task", ""))
    readiness_status = str(readiness.get("status", ""))
    readiness_next_owner = str(readiness.get("next_owner", ""))
    if readiness_task and readiness_task != task:
        errors.append("Bundle readiness task does not match the embedded handover task.")
    if readiness_status and readiness_status != status:
        errors.append("Bundle readiness status does not match the embedded handover status.")
    if readiness_next_owner and readiness_next_owner != next_owner:
        errors.append("Bundle readiness next owner does not match the embedded handover next owner.")

    with tempfile.TemporaryDirectory(prefix="inspect-handoff-bundle-") as tmp_dir_name:
        docs_root = Path(tmp_dir_name) / "docs" / "tests"
        handover_path, session_path = stage_bundle_documents(bundle, docs_root)

        errors.extend(f"HANDOVER: {error}" for error in validate_handover_document(handover_path))
        errors.extend(f"SESSION: {error}" for error in validate_session_document(session_path))
        if not any(error.startswith("HANDOVER:") or error.startswith("SESSION:") for error in errors):
            staged_handover_sections = parse_markdown(handover_path, HANDOVER_ROOT, parse_handover_sections)
            staged_session_sections = parse_markdown(session_path, SESSION_ROOT, parse_session_sections)
            errors.extend(
                f"PAIR: {error}"
                for error in collect_pair_errors(
                    handover_path=handover_path,
                    session_path=session_path,
                    handover_sections=staged_handover_sections,
                    session_sections=staged_session_sections,
                )
            )

        lease_payload = lease.get("payload")
        lease_present = isinstance(lease_payload, dict)
        lease_state = "none"
        if lease_present:
            lease_errors, lease_warnings, normalized_lease = validate_lease_payload(docs_root, lease_payload)
            errors.extend(f"LEASE: {error}" for error in lease_errors)
            warnings.extend(f"LEASE: {warning}" for warning in lease_warnings)
            lease_path = lease_path_for_docs_root(docs_root)
            lease_path.parent.mkdir(parents=True, exist_ok=True)
            lease_path.write_text(json.dumps(lease_payload, indent=2) + "\n", encoding="utf-8")
            lease_state = str(normalized_lease["state"])

    source_report_result = str(report.get("result", "unknown"))
    source_readiness_verdict = str(readiness.get("verdict", "unknown"))
    source_report_warnings = report.get("warnings", [])
    source_report_errors = report.get("errors", [])
    if isinstance(source_report_warnings, list):
        warnings.extend(f"SOURCE-WORKSPACE: {warning}" for warning in source_report_warnings)
    if isinstance(source_report_errors, list):
        warnings.extend(f"SOURCE-WORKSPACE: {error}" for error in source_report_errors)
    if source_readiness_verdict not in {"unknown", "ready"}:
        warnings.append(f"SOURCE: Bundle was exported from a workspace with readiness verdict {source_readiness_verdict}.")

    result = "valid"
    if warnings:
        result = "valid-with-warnings"
    if errors:
        result = "error"

    return {
        "result": result,
        "bundle_path": str(bundle_path),
        "bundle_version": BUNDLE_VERSION,
        "exported_at": str(bundle.get("exported_at", "unknown")),
        "source_resolution": str(source.get("resolution", "unknown")),
        "source_docs_root": str(source.get("docs_root", "unknown")),
        "handover_name": handover_name,
        "session_state_name": session_name,
        "task": task,
        "status": status,
        "last_updated": last_updated,
        "updated_by": updated_by,
        "next_owner": next_owner,
        "lease_present": lease_present,
        "lease_state": lease_state,
        "signature_present": bool(signature),
        "signature_scheme": str(signature.get("scheme", "None")) if signature else "None",
        "signature_signer": str(signature.get("signer", "None")) if signature else "None",
        "signature_key_id": str(signature.get("key_id", "None")) if signature else "None",
        "signature_public_key_fingerprint": str(signature.get("public_key_fingerprint", "None")) if signature else "None",
        "signature_signed_at": str(signature.get("signed_at", "None")) if signature else "None",
        "git_available": bool(git.get("available")) if git else False,
        "git_branch": str(git.get("branch", "None")) if git else "None",
        "git_commit_sha": str(git.get("commit_sha", "None")) if git else "None",
        "git_dirty": bool(git.get("is_dirty")) if git else False,
        "git_dirty_fingerprint": str(git.get("dirty_fingerprint", "None")) if git else "None",
        "git_status_fingerprint": str(git.get("status_fingerprint", "None")) if git else "None",
        "git_patch_summary_fingerprint": str(git.get("patch_summary_fingerprint", "None")) if git else "None",
        "git_changed_file_count": int(git.get("changed_file_count", 0)) if git else 0,
        "git_added_line_count": int(git.get("added_line_count", 0)) if git else 0,
        "git_deleted_line_count": int(git.get("deleted_line_count", 0)) if git else 0,
        "redaction_enabled": bool(redaction.get("enabled")) if redaction else False,
        "redaction_count": int(redaction.get("redaction_count", 0)) if redaction else 0,
        "redaction_policy_source": str(redaction.get("policy_source", "None")) if redaction else "None",
        "source_report_result": source_report_result,
        "source_readiness_verdict": source_readiness_verdict,
        "warnings": warnings,
        "errors": errors,
    }


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Bundle: {payload['bundle_path']}",
        f"Bundle version: {payload['bundle_version']}",
        f"Exported at: {payload['exported_at']}",
        f"Source resolution: {payload['source_resolution']}",
        f"Source docs root: {payload['source_docs_root']}",
        f"Task: {payload['task']}",
        f"Status: {payload['status']}",
        f"Last updated: {payload['last_updated']}",
        f"Updated by: {payload['updated_by']}",
        f"Next owner: {payload['next_owner']}",
        f"Handover name: {payload['handover_name']}",
        f"Session-state name: {payload['session_state_name']}",
        f"Lease present: {payload['lease_present']}",
        f"Lease state: {payload['lease_state']}",
        f"Signature present: {payload['signature_present']}",
        f"Signature scheme: {payload['signature_scheme']}",
        f"Signature signer: {payload['signature_signer']}",
        f"Signature key id: {payload['signature_key_id']}",
        f"Signature public key fingerprint: {payload['signature_public_key_fingerprint']}",
        f"Signature signed at: {payload['signature_signed_at']}",
        f"Git available: {payload['git_available']}",
        f"Git branch: {payload['git_branch']}",
        f"Git commit: {payload['git_commit_sha']}",
        f"Git dirty: {payload['git_dirty']}",
        f"Git dirty fingerprint: {payload['git_dirty_fingerprint']}",
        f"Git status fingerprint: {payload['git_status_fingerprint']}",
        f"Git patch summary fingerprint: {payload['git_patch_summary_fingerprint']}",
        f"Git changed file count: {payload['git_changed_file_count']}",
        f"Git added line count: {payload['git_added_line_count']}",
        f"Git deleted line count: {payload['git_deleted_line_count']}",
        f"Redaction enabled: {payload['redaction_enabled']}",
        f"Redaction count: {payload['redaction_count']}",
        f"Redaction policy source: {payload['redaction_policy_source']}",
        f"Source report result: {payload['source_report_result']}",
        f"Source readiness verdict: {payload['source_readiness_verdict']}",
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


def main() -> int:
    args = parse_args()
    bundle_path = Path(args.bundle).resolve()
    if not bundle_path.exists():
        payload = {
            "result": "error",
            "bundle_path": str(bundle_path),
            "bundle_version": BUNDLE_VERSION,
            "exported_at": "unknown",
            "source_resolution": "unknown",
            "source_docs_root": "unknown",
            "handover_name": "unknown",
            "session_state_name": "unknown",
            "task": "unknown",
            "status": "unknown",
            "last_updated": "unknown",
            "updated_by": "unknown",
            "next_owner": "unknown",
            "lease_present": False,
            "lease_state": "unknown",
            "signature_present": False,
            "signature_scheme": "unknown",
            "signature_signer": "unknown",
            "signature_key_id": "unknown",
            "signature_public_key_fingerprint": "unknown",
            "signature_signed_at": "unknown",
            "git_available": False,
            "git_branch": "unknown",
            "git_commit_sha": "unknown",
            "git_dirty": False,
            "git_dirty_fingerprint": "unknown",
            "git_status_fingerprint": "unknown",
            "git_patch_summary_fingerprint": "unknown",
            "git_changed_file_count": 0,
            "git_added_line_count": 0,
            "git_deleted_line_count": 0,
            "redaction_enabled": False,
            "redaction_count": 0,
            "redaction_policy_source": "unknown",
            "source_report_result": "unknown",
            "source_readiness_verdict": "unknown",
            "warnings": [],
            "errors": [f"Bundle does not exist: {bundle_path}"],
        }
    else:
        try:
            payload = build_bundle_payload(bundle_path)
        except ValueError as exc:
            payload = {
                "result": "error",
                "bundle_path": str(bundle_path),
                "bundle_version": BUNDLE_VERSION,
                "exported_at": "unknown",
                "source_resolution": "unknown",
                "source_docs_root": "unknown",
                "handover_name": "unknown",
                "session_state_name": "unknown",
                "task": "unknown",
                "status": "unknown",
                "last_updated": "unknown",
                "updated_by": "unknown",
                "next_owner": "unknown",
                "lease_present": False,
                "lease_state": "unknown",
                "signature_present": False,
                "signature_scheme": "unknown",
                "signature_signer": "unknown",
                "signature_key_id": "unknown",
                "signature_public_key_fingerprint": "unknown",
                "signature_signed_at": "unknown",
                "git_available": False,
                "git_branch": "unknown",
                "git_commit_sha": "unknown",
                "git_dirty": False,
                "git_dirty_fingerprint": "unknown",
                "git_status_fingerprint": "unknown",
                "git_patch_summary_fingerprint": "unknown",
                "git_changed_file_count": 0,
                "git_added_line_count": 0,
                "git_deleted_line_count": 0,
                "redaction_enabled": False,
                "redaction_count": 0,
                "redaction_policy_source": "unknown",
                "source_report_result": "unknown",
                "source_readiness_verdict": "unknown",
                "warnings": [],
                "errors": [str(exc)],
            }

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(payload))

    if payload["errors"]:
        return 1
    if args.strict and payload["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
