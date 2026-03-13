#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from handoff_bundle_trust import (  # type: ignore
    build_trust_payload,
    default_trust_policy,
    load_trust_policy_file,
    merge_trust_policy,
    resolve_trust_policy_path,
)
from handoff_bundle import load_bundle, resolve_signing_secret  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply a deterministic trust policy to a portable handoff bundle before import."
    )
    parser.add_argument("--bundle", required=True, help="Path to the exported handoff bundle JSON file.")
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root used for trust policy discovery.")
    parser.add_argument("--policy-file", help="Explicit trust policy JSON file. Defaults to docs/tests/handoff-bundle-trust-policy.json when present.")
    parser.add_argument("--policy-profile", help="Optional trust-policy profile to apply from the checked-in or explicit policy file.")
    parser.add_argument("--no-policy-file", action="store_true", help="Ignore the default trust policy file discovery and use only built-in defaults plus CLI overrides.")
    parser.add_argument("--allow-inspection-warnings", action="store_true", help="Allow bundles that inspect as valid-with-warnings.")
    parser.add_argument("--allow-source-not-ready", action="store_true", help="Allow bundles exported from active not-ready workspaces.")
    parser.add_argument("--allow-active-lease", action="store_true", help="Allow bundles that carry an active lease.")
    parser.add_argument("--allow-expired-lease", action="store_true", help="Allow bundles that carry an expired lease.")
    parser.add_argument("--max-age-hours", type=int, help="Maximum allowed bundle age in hours.")
    parser.add_argument("--allowed-updated-by", action="append", help="Repeat to allow only specific Updated by values.")
    parser.add_argument("--allowed-next-owner", action="append", help="Repeat to allow only specific Next owner values.")
    parser.add_argument("--require-signature", action="store_true", help="Require a verified bundle signature.")
    parser.add_argument("--allowed-signature-scheme", action="append", help="Repeat to allow only specific signature schemes.")
    parser.add_argument("--allowed-signer", action="append", help="Repeat to allow only specific signature signer values.")
    parser.add_argument("--allowed-key-id", action="append", help="Repeat to allow only specific signature key id values.")
    parser.add_argument("--allowed-public-key-fingerprint", action="append", help="Repeat to allow only specific SSH public key fingerprints.")
    parser.add_argument("--revoked-signer", action="append", help="Repeat to reject revoked signature signer values.")
    parser.add_argument("--revoked-key-id", action="append", help="Repeat to reject revoked signature key id values.")
    parser.add_argument("--revoked-public-key-fingerprint", action="append", help="Repeat to reject revoked SSH public key fingerprints.")
    parser.add_argument("--secret-file", help="Path to a file containing the signature verification secret.")
    parser.add_argument("--secret-env", help="Environment variable that contains the signature verification secret when --secret-file is omitted. Defaults to the policy value or HANDOFF_BUNDLE_SIGNING_SECRET.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--strict-warnings", action="store_true", help="Return a non-zero exit code when warnings are present.")
    return parser.parse_args()


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Bundle: {payload['bundle_path']}",
        f"Task: {payload['task']}",
        f"Status: {payload['status']}",
        f"Updated by: {payload['updated_by']}",
        f"Next owner: {payload['next_owner']}",
        f"Exported at: {payload['exported_at']}",
        f"Lease state: {payload['lease_state']}",
        f"Source readiness verdict: {payload['source_readiness_verdict']}",
        f"Policy source: {payload['policy_source']}",
        f"Signature present: {payload['signature_present']}",
        f"Signature scheme: {payload['signature_scheme']}",
        f"Signature signer: {payload['signature_signer']}",
        f"Signature key id: {payload['signature_key_id']}",
        f"Signature public key fingerprint: {payload['signature_public_key_fingerprint']}",
        f"Signature verified: {payload['signature_verified']}",
        "Warnings:",
    ]
    warnings = payload["warnings"]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")
    lines.append("Blocking reasons:")
    blocking_reasons = payload["blocking_reasons"]
    if blocking_reasons:
        lines.extend(f"- {reason}" for reason in blocking_reasons)
    else:
        lines.append("- None")
    lines.append("Next actions:")
    next_actions = payload["next_actions"]
    if next_actions:
        lines.extend(f"{index}. {action}" for index, action in enumerate(next_actions, start=1))
    else:
        lines.append("1. None")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    bundle_path = Path(args.bundle).resolve()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    try:
        policy_path = resolve_trust_policy_path(
            start_dir=start_dir,
            explicit_root=args.root,
            explicit_policy_path=args.policy_file,
            use_default_policy_file=not args.no_policy_file,
        )
        base_policy = load_trust_policy_file(policy_path, args.policy_profile) if policy_path else default_trust_policy()
    except ValueError as exc:
        payload = {
            "result": "untrusted",
            "bundle_path": str(bundle_path),
            "task": "unknown",
            "status": "unknown",
            "updated_by": "unknown",
            "next_owner": "unknown",
            "exported_at": "unknown",
            "lease_state": "unknown",
            "source_readiness_verdict": "unknown",
            "policy_source": str(policy_path) if 'policy_path' in locals() and policy_path else "default",
            "signature_present": False,
            "signature_scheme": "unknown",
            "signature_signer": "unknown",
            "signature_key_id": "unknown",
            "signature_public_key_fingerprint": "unknown",
            "signature_verified": False,
            "policy": {},
            "warnings": [],
            "blocking_reasons": [str(exc)],
            "next_actions": [
                "Fix the trust policy JSON file or pass --no-policy-file to ignore it."
            ],
            "inspection": None,
        }
        if args.format == "json":
            print(json.dumps(payload, indent=2))
        else:
            print(format_text(payload))
        return 1

    policy = merge_trust_policy(
        base_policy,
        allow_inspection_warnings=args.allow_inspection_warnings,
        allow_source_not_ready=args.allow_source_not_ready,
        allow_active_lease=args.allow_active_lease,
        allow_expired_lease=args.allow_expired_lease,
        max_age_hours=args.max_age_hours,
        allowed_updated_by=args.allowed_updated_by,
        allowed_next_owner=args.allowed_next_owner,
        require_signature=args.require_signature,
        allowed_signature_schemes=args.allowed_signature_scheme,
        allowed_signers=args.allowed_signer,
        allowed_key_ids=args.allowed_key_id,
        allowed_public_key_fingerprints=args.allowed_public_key_fingerprint,
        revoked_signers=args.revoked_signer,
        revoked_key_ids=args.revoked_key_id,
        revoked_public_key_fingerprints=args.revoked_public_key_fingerprint,
    )
    policy_source = str(policy_path) if policy_path else "default"
    verification_secret = None
    try:
        bundle = load_bundle(bundle_path)
    except ValueError as exc:
        payload = {
            "result": "untrusted",
            "bundle_path": str(bundle_path),
            "task": "unknown",
            "status": "unknown",
            "updated_by": "unknown",
            "next_owner": "unknown",
            "exported_at": "unknown",
            "lease_state": "unknown",
            "source_readiness_verdict": "unknown",
            "policy_source": policy_source,
            "signature_present": False,
            "signature_scheme": "unknown",
            "signature_signer": "unknown",
            "signature_key_id": "unknown",
            "signature_public_key_fingerprint": "unknown",
            "signature_verified": False,
            "policy": policy,
            "warnings": [],
            "blocking_reasons": [str(exc)],
            "next_actions": [
                "Run python ../shared/scripts/inspect_handoff_bundle.py --bundle <handoff-bundle.json> --format text and fix the reported bundle errors."
            ],
            "inspection": None,
        }
        if args.format == "json":
            print(json.dumps(payload, indent=2))
        else:
            print(format_text(payload))
        return 1
    signature = bundle.get("signature") if isinstance(bundle.get("signature"), dict) else {}
    needs_signature_secret = bool(signature) and str(signature.get("scheme", "")).strip() == "hmac-sha256" and (
        bool(policy["require_signature"])
        or bool(policy["allowed_signature_schemes"])
        or bool(policy["allowed_signers"])
        or bool(policy["allowed_key_ids"])
        or bool(policy["allowed_public_key_fingerprints"])
        or bool(policy["revoked_signers"])
        or bool(policy["revoked_key_ids"])
        or bool(policy["revoked_public_key_fingerprints"])
    )
    if needs_signature_secret:
        try:
            verification_secret = resolve_signing_secret(
                secret_file=args.secret_file,
                secret_env=args.secret_env or policy.get("signature_secret_env") or "HANDOFF_BUNDLE_SIGNING_SECRET",
            )
        except ValueError as exc:
            payload = {
                "result": "untrusted",
                "bundle_path": str(bundle_path),
                "task": "unknown",
                "status": "unknown",
                "updated_by": "unknown",
                "next_owner": "unknown",
                "exported_at": "unknown",
                "lease_state": "unknown",
                "source_readiness_verdict": "unknown",
                "policy_source": policy_source,
                "signature_present": False,
                "signature_scheme": "unknown",
                "signature_signer": "unknown",
                "signature_key_id": "unknown",
                "signature_public_key_fingerprint": "unknown",
                "signature_verified": False,
                "policy": policy,
                "warnings": [],
                "blocking_reasons": [str(exc)],
                "next_actions": [
                    "Pass --secret-file <path> or set HANDOFF_BUNDLE_SIGNING_SECRET before applying signature trust checks."
                ],
                "inspection": None,
            }
            if args.format == "json":
                print(json.dumps(payload, indent=2))
            else:
                print(format_text(payload))
            return 1

    payload = build_trust_payload(
        bundle_path,
        policy,
        verification_secret=verification_secret,
        policy_source=policy_source,
    )
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(payload))

    if payload["result"] == "untrusted":
        return 1
    if args.strict_warnings and payload["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
