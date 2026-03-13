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

from check_handoff_readiness import build_readiness_payload  # type: ignore  # noqa: E402
from handoff_bundle import (  # type: ignore  # noqa: E402
    BUNDLE_VERSION,
    load_bundle,
    require_mapping,
    require_string,
    resolve_signing_secret,
    validate_bundle_documents,
)
from handoff_bundle_trust import (  # type: ignore  # noqa: E402
    build_trust_payload,
    default_trust_policy,
    load_trust_policy_file,
    merge_trust_policy,
    resolve_trust_policy_path,
)
from handoff_lease import (  # type: ignore  # noqa: E402
    inspect_lease,
    lease_path_for_docs_root,
    relative_pointer as lease_relative_pointer,
)
from reconcile_handoff_pair import relative_pointer, write_markdown  # type: ignore  # noqa: E402
from report_handoff_workspace import build_workspace_report  # type: ignore  # noqa: E402
from resolve_test_docs_root import ensure_dirs, resolve_docs_root  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    REQUIRED_SECTIONS as HANDOVER_SECTIONS,
    extract_status as extract_handover_status,
    parse_sections as parse_handover_sections,
    validate_document as validate_handover_document,
)
from validate_handoff_pair import collect_pair_errors, parse_markdown  # type: ignore  # noqa: E402
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    REQUIRED_SECTIONS as SESSION_SECTIONS,
    parse_sections as parse_session_sections,
    validate_document as validate_session_document,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a portable handoff bundle into the target workspace and restore the linked pair deterministically."
    )
    parser.add_argument("--bundle", required=True, help="Path to the exported handoff bundle JSON file.")
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--handover-output", help="Optional explicit output path for the imported handover file.")
    parser.add_argument("--session-output", help="Optional explicit output path for the imported session-state file. Defaults to CURRENT.md.")
    parser.add_argument("--strip-lease", action="store_true", help="Do not restore the exported lease; ensure no lease file remains after import.")
    parser.add_argument("--trusted-only", action="store_true", help="Require the bundle to pass the default conservative trust policy before restoring it.")
    parser.add_argument("--policy-file", help="Explicit trust policy JSON file. Defaults to docs/tests/handoff-bundle-trust-policy.json when present.")
    parser.add_argument("--policy-profile", help="Optional trust-policy profile to apply from the checked-in or explicit policy file.")
    parser.add_argument("--no-policy-file", action="store_true", help="Ignore the default trust policy file discovery and use only built-in defaults plus CLI overrides.")
    parser.add_argument("--require-signature", action="store_true", help="With --trusted-only, require a verified bundle signature before restoring.")
    parser.add_argument("--allowed-signature-scheme", action="append", help="With --trusted-only, allow only specific signature schemes.")
    parser.add_argument("--allowed-signer", action="append", help="With --trusted-only, allow only specific signature signer values.")
    parser.add_argument("--allowed-key-id", action="append", help="With --trusted-only, allow only specific signature key id values.")
    parser.add_argument("--allowed-public-key-fingerprint", action="append", help="With --trusted-only, allow only specific SSH public key fingerprints.")
    parser.add_argument("--revoked-signer", action="append", help="With --trusted-only, reject revoked signature signer values.")
    parser.add_argument("--revoked-key-id", action="append", help="With --trusted-only, reject revoked signature key id values.")
    parser.add_argument("--revoked-public-key-fingerprint", action="append", help="With --trusted-only, reject revoked SSH public key fingerprints.")
    parser.add_argument("--secret-file", help="Path to a file containing the signature verification secret for --trusted-only.")
    parser.add_argument("--secret-env", help="Environment variable that contains the signature verification secret when --secret-file is omitted. Defaults to the policy value or HANDOFF_BUNDLE_SIGNING_SECRET.")
    parser.add_argument("--dry-run", action="store_true", help="Preview the exact files, pointers, and lease data that would be written without modifying the workspace.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing target files if they already exist.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Bundle: {payload['bundle_path']}",
        f"Docs root: {payload['docs_root']}",
        f"Handover: {payload['handover']}",
        f"Session-state: {payload['session_state']}",
        f"Status: {payload['status']}",
        f"Next owner: {payload['next_owner']}",
        f"Lease restored: {payload['lease_restored']}",
        f"Lease state: {payload['lease_state']}",
        f"Source readiness verdict: {payload['source_readiness_verdict']}",
        f"Dry run: {payload.get('dry_run', False)}",
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


def shadow_path(temp_root: Path, original: Path) -> Path:
    drive = original.drive.rstrip(":") or "root"
    relative_parts = list(original.parts[1:]) if original.anchor else list(original.parts)
    return temp_root / drive / Path(*relative_parts)


def validate_materialized_import(
    *,
    docs_root: Path,
    handover_path: Path,
    session_path: Path,
    lease_path: Path,
    handover_sections: dict[str, str],
    session_sections: dict[str, str],
    lease_payload: dict[str, object] | None,
) -> tuple[list[str], list[str], dict[str, object]]:
    target_handover = handover_path
    target_session = session_path
    target_lease = lease_path

    target_handover.parent.mkdir(parents=True, exist_ok=True)
    target_session.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(target_handover, HANDOVER_ROOT, HANDOVER_SECTIONS, handover_sections)
    write_markdown(target_session, SESSION_ROOT, SESSION_SECTIONS, session_sections)

    if lease_payload is None:
        if target_lease.exists():
            target_lease.unlink()
    else:
        target_lease.parent.mkdir(parents=True, exist_ok=True)
        target_lease.write_text(json.dumps(lease_payload, indent=2) + "\n", encoding="utf-8")

    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(f"HANDOVER: {error}" for error in validate_handover_document(target_handover))
    errors.extend(f"SESSION: {error}" for error in validate_session_document(target_session))

    if not errors:
        imported_handover_sections = parse_markdown(target_handover, HANDOVER_ROOT, parse_handover_sections)
        imported_session_sections = parse_markdown(target_session, SESSION_ROOT, parse_session_sections)
        errors.extend(
            f"PAIR: {error}"
            for error in collect_pair_errors(
                handover_path=target_handover,
                session_path=target_session,
                handover_sections=imported_handover_sections,
                session_sections=imported_session_sections,
            )
        )

    lease_inspection = inspect_lease(start_dir=docs_root, explicit_root=str(docs_root))
    warnings.extend(f"LEASE: {warning}" for warning in lease_inspection["warnings"])
    errors.extend(f"LEASE: {error}" for error in lease_inspection["errors"])
    return errors, warnings, lease_inspection


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    bundle_path = Path(args.bundle).resolve()

    if not bundle_path.exists():
        payload = {
            "result": "error",
            "bundle_path": str(bundle_path),
            "docs_root": "None",
            "handover": "None",
            "session_state": "None",
            "status": "unknown",
            "next_owner": "unknown",
            "lease_restored": False,
            "lease_state": "unknown",
            "source_readiness_verdict": "unknown",
            "warnings": [],
            "errors": [f"Bundle does not exist: {bundle_path}"],
        }
        return emit(payload, args.format)

    if args.trusted_only:
        try:
            policy_path = resolve_trust_policy_path(
                start_dir=start_dir,
                explicit_root=args.root,
                explicit_policy_path=args.policy_file,
                use_default_policy_file=not args.no_policy_file,
            )
            base_policy = load_trust_policy_file(policy_path, args.policy_profile) if policy_path else default_trust_policy()
            trust_policy = merge_trust_policy(
                base_policy,
                require_signature=args.require_signature,
                allowed_signature_schemes=args.allowed_signature_scheme,
                allowed_signers=args.allowed_signer,
                allowed_key_ids=args.allowed_key_id,
                allowed_public_key_fingerprints=args.allowed_public_key_fingerprint,
                revoked_signers=args.revoked_signer,
                revoked_key_ids=args.revoked_key_id,
                revoked_public_key_fingerprints=args.revoked_public_key_fingerprint,
            )
            verification_secret = None
            bundle = load_bundle(bundle_path)
            signature = bundle.get("signature") if isinstance(bundle.get("signature"), dict) else {}
            if signature and str(signature.get("scheme", "")).strip() == "hmac-sha256" and (
                trust_policy["require_signature"]
                or trust_policy["allowed_signature_schemes"]
                or trust_policy["allowed_signers"]
                or trust_policy["allowed_key_ids"]
                or trust_policy["allowed_public_key_fingerprints"]
                or trust_policy["revoked_signers"]
                or trust_policy["revoked_key_ids"]
                or trust_policy["revoked_public_key_fingerprints"]
            ):
                verification_secret = resolve_signing_secret(
                    secret_file=args.secret_file,
                    secret_env=args.secret_env or trust_policy.get("signature_secret_env") or "HANDOFF_BUNDLE_SIGNING_SECRET",
                )
        except ValueError as exc:
            payload = {
                "result": "error",
                "bundle_path": str(bundle_path),
                "docs_root": "None",
                "handover": "None",
                "session_state": "None",
                "status": "unknown",
                "next_owner": "unknown",
                "lease_restored": False,
                "lease_state": "unknown",
                "source_readiness_verdict": "unknown",
                "warnings": [],
                "errors": [str(exc)],
            }
            return emit(payload, args.format)
        trust_payload = build_trust_payload(
            bundle_path,
            trust_policy,
            verification_secret=verification_secret,
            policy_source=str(policy_path) if policy_path else "default",
        )
        if trust_payload["result"] == "untrusted":
            payload = {
                "result": "error",
                "bundle_path": str(bundle_path),
                "docs_root": "None",
                "handover": "None",
                "session_state": "None",
                "status": "unknown",
                "next_owner": "unknown",
                "lease_restored": False,
                "lease_state": str(trust_payload["lease_state"]),
                "source_readiness_verdict": str(trust_payload["source_readiness_verdict"]),
                "warnings": list(trust_payload["warnings"]),
                "errors": list(trust_payload["blocking_reasons"]),
                "trust": trust_payload,
            }
            return emit(payload, args.format)
    else:
        trust_payload = None

    try:
        bundle = load_bundle(bundle_path)
        handover_sections, session_sections = validate_bundle_documents(bundle)
        docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    except ValueError as exc:
        payload = {
            "result": "error",
            "bundle_path": str(bundle_path),
            "docs_root": "None",
            "handover": "None",
            "session_state": "None",
            "status": "unknown",
            "next_owner": "unknown",
            "lease_restored": False,
            "lease_state": "unknown",
            "source_readiness_verdict": "unknown",
            "warnings": [],
            "errors": [str(exc)],
        }
        return emit(payload, args.format)

    ensure_dirs(docs_root, "both")
    source = require_mapping(bundle["source"], "Bundle source")
    target_handover = (
        Path(args.handover_output).resolve()
        if args.handover_output
        else (docs_root / "handovers" / str(source["handover_name"])).resolve()
    )
    target_session = (
        Path(args.session_output).resolve()
        if args.session_output
        else (docs_root / "session-state" / "CURRENT.md").resolve()
    )
    target_lease = lease_path_for_docs_root(docs_root).resolve()

    if target_handover == target_session:
        payload = {
            "result": "error",
            "bundle_path": str(bundle_path),
            "docs_root": str(docs_root),
            "handover": str(target_handover),
            "session_state": str(target_session),
            "status": "unknown",
            "next_owner": "unknown",
            "lease_restored": False,
            "lease_state": "unknown",
            "source_readiness_verdict": "unknown",
            "warnings": [],
            "errors": ["Imported handover and session-state outputs must be different files."],
        }
        return emit(payload, args.format)

    protected_paths = [path for path in (target_handover, target_session, target_lease) if path.exists()]
    if protected_paths and not args.force and not args.dry_run:
        payload = {
            "result": "error",
            "bundle_path": str(bundle_path),
            "docs_root": str(docs_root),
            "handover": str(target_handover),
            "session_state": str(target_session),
            "status": "unknown",
            "next_owner": "unknown",
            "lease_restored": False,
            "lease_state": "unknown",
            "source_readiness_verdict": "unknown",
            "warnings": [],
            "errors": [f"Refusing to overwrite existing file: {path}" for path in protected_paths],
        }
        return emit(payload, args.format)

    status = extract_handover_status(handover_sections)
    handover_sections["Session-state pointer"] = "None" if status == "done" else relative_pointer(target_handover, target_session)
    session_sections["Handover pointer"] = relative_pointer(target_session, target_handover)

    lease_block = require_mapping(bundle["lease"], "Bundle lease")
    lease_restored = False
    lease_payload_to_write: dict[str, object] | None = None
    if args.strip_lease or lease_block.get("payload") is None:
        lease_payload_to_write = None
    else:
        lease_payload = dict(require_mapping(lease_block["payload"], "Bundle lease payload"))
        lease_payload["handover"] = lease_relative_pointer(docs_root, target_handover)
        lease_payload["session_state"] = lease_relative_pointer(docs_root, target_session)
        lease_payload_to_write = lease_payload
        lease_restored = True

    if args.dry_run:
        with tempfile.TemporaryDirectory(prefix="import-handoff-preview-") as tmp_dir_name:
            temp_root = Path(tmp_dir_name)
            shadow_docs_root = shadow_path(temp_root, docs_root)
            shadow_handover = shadow_path(temp_root, target_handover)
            shadow_session = shadow_path(temp_root, target_session)
            shadow_lease = shadow_path(temp_root, target_lease)
            shadow_lease_payload = None
            if lease_payload_to_write is not None:
                shadow_lease_payload = dict(lease_payload_to_write)
            errors, warnings, lease_inspection = validate_materialized_import(
                docs_root=shadow_docs_root,
                handover_path=shadow_handover,
                session_path=shadow_session,
                lease_path=shadow_lease,
                handover_sections=dict(handover_sections),
                session_sections=dict(session_sections),
                lease_payload=shadow_lease_payload,
            )
    else:
        errors, warnings, lease_inspection = validate_materialized_import(
            docs_root=docs_root,
            handover_path=target_handover,
            session_path=target_session,
            lease_path=target_lease,
            handover_sections=dict(handover_sections),
            session_sections=dict(session_sections),
            lease_payload=lease_payload_to_write,
        )

    source_readiness_raw = bundle.get("readiness")
    source_readiness = source_readiness_raw if isinstance(source_readiness_raw, dict) else {}
    source_readiness_verdict = str(source_readiness.get("verdict", "unknown"))
    if source_readiness_verdict not in {"unknown", "ready"}:
        warnings.append(f"SOURCE: Bundle was exported from a workspace with readiness verdict {source_readiness_verdict}.")

    report = None
    if not errors and not args.dry_run:
        try:
            report = build_workspace_report(start_dir=docs_root, explicit_root=str(docs_root), history_limit=3)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            warnings.extend(f"WORKSPACE: {warning}" for warning in report["warnings"])
            errors.extend(f"WORKSPACE: {error}" for error in report["errors"])
    if args.dry_run and protected_paths:
        warnings.append(
            "TARGETS: Existing files would block a real import without --force: "
            + ", ".join(str(path) for path in protected_paths)
        )

    if args.dry_run:
        result = "preview-with-warnings" if warnings else "preview"
    else:
        result = "imported-with-warnings" if warnings else "imported"
    if errors:
        result = "error"

    next_owner = report["summary"]["next_owner"] if report is not None else session_sections.get("Next owner", "unknown")
    payload = {
        "result": result,
        "bundle_path": str(bundle_path),
        "docs_root": str(docs_root),
        "handover": str(target_handover),
        "session_state": str(target_session),
        "status": status,
        "next_owner": next_owner,
        "lease_restored": lease_restored,
        "lease_state": lease_inspection["state"],
        "source_readiness_verdict": source_readiness_verdict,
        "dry_run": args.dry_run,
        "would_overwrite": [str(path) for path in protected_paths],
        "would_write": {
            "handover": str(target_handover),
            "session_state": str(target_session),
            "lease": str(target_lease),
        },
        "warnings": warnings,
        "errors": errors,
    }

    if report is not None:
        payload["report"] = report
        payload["readiness"] = build_readiness_payload(report)
    if trust_payload is not None:
        payload["trust"] = trust_payload

    return emit(payload, args.format)


if __name__ == "__main__":
    raise SystemExit(main())
