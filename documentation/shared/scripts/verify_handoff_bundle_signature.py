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

from handoff_bundle import (  # type: ignore  # noqa: E402
    load_bundle,
    resolve_signing_secret,
    verify_bundle_signature,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the signature on a portable handoff bundle.")
    parser.add_argument("--bundle", required=True, help="Path to the exported handoff bundle JSON file.")
    parser.add_argument("--secret-file", help="Path to a file containing the signing secret.")
    parser.add_argument("--secret-env", default="HANDOFF_BUNDLE_SIGNING_SECRET", help="Environment variable that contains the signing secret when --secret-file is omitted.")
    parser.add_argument("--required-signer", help="Optional signer that must match the bundle signature.")
    parser.add_argument("--required-key-id", help="Optional key id that must match the bundle signature.")
    parser.add_argument("--required-scheme", choices=("hmac-sha256", "sshsig"), help="Optional signature scheme that must match the bundle signature.")
    parser.add_argument("--required-public-key-fingerprint", help="Optional SSH public key fingerprint that must match the bundle signature.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Bundle: {payload['bundle_path']}",
        f"Signer: {payload['signer']}",
        f"Key id: {payload['key_id']}",
        f"Scheme: {payload['scheme']}",
        f"Public key fingerprint: {payload['public_key_fingerprint']}",
        f"Signed at: {payload['signed_at']}",
        "Errors:",
    ]
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
    bundle_path = Path(args.bundle).resolve()
    payload = {
        "result": "error",
        "bundle_path": str(bundle_path),
        "signer": "unknown",
        "key_id": "unknown",
        "scheme": "unknown",
        "public_key_fingerprint": "unknown",
        "signed_at": "unknown",
        "errors": [],
    }

    if not bundle_path.exists():
        payload["errors"] = [f"Bundle does not exist: {bundle_path}"]
        return emit(payload, args.format)

    try:
        bundle = load_bundle(bundle_path)
        signature = bundle.get("signature") if isinstance(bundle.get("signature"), dict) else {}
        payload["signer"] = str(signature.get("signer", "unknown"))
        payload["key_id"] = str(signature.get("key_id", "unknown"))
        payload["scheme"] = str(signature.get("scheme", "unknown"))
        payload["public_key_fingerprint"] = str(signature.get("public_key_fingerprint", "unknown"))
        payload["signed_at"] = str(signature.get("signed_at", "unknown"))
        secret = None
        if payload["scheme"] == "hmac-sha256":
            secret = resolve_signing_secret(secret_file=args.secret_file, secret_env=args.secret_env)
        errors = verify_bundle_signature(
            bundle,
            secret,
            required_signer=args.required_signer,
            required_key_id=args.required_key_id,
            required_scheme=args.required_scheme,
            required_public_key_fingerprint=args.required_public_key_fingerprint,
        )
    except ValueError as exc:
        payload["errors"] = [str(exc)]
        return emit(payload, args.format)

    payload["errors"] = errors
    payload["result"] = "verified" if not errors else "error"
    return emit(payload, args.format)


if __name__ == "__main__":
    raise SystemExit(main())
