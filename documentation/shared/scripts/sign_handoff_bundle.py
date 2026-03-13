#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"

if str(SHARED_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SHARED_SCRIPTS))

from handoff_bundle import (  # type: ignore  # noqa: E402
    attach_bundle_signature,
    load_bundle,
    resolve_signing_secret,
    resolve_ssh_public_key,
)


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sign a portable handoff bundle with either an HMAC or SSH signature.")
    parser.add_argument("--bundle", required=True, help="Path to the exported handoff bundle JSON file.")
    parser.add_argument("--signer", required=True, help="Identifier for the human or AI signing the bundle.")
    parser.add_argument("--key-id", required=True, help="Identifier for the signing secret or trust domain.")
    parser.add_argument("--scheme", choices=("hmac-sha256", "sshsig"), default="hmac-sha256", help="Signature scheme to apply to the bundle.")
    parser.add_argument("--secret-file", help="Path to a file containing the signing secret.")
    parser.add_argument("--secret-env", default="HANDOFF_BUNDLE_SIGNING_SECRET", help="Environment variable that contains the signing secret when --secret-file is omitted.")
    parser.add_argument("--private-key-file", help="Path to an SSH private key used for asymmetric bundle signing.")
    parser.add_argument("--public-key-file", help="Optional explicit SSH public key file. Defaults to <private-key-file>.pub.")
    parser.add_argument("--signed-at", default=current_timestamp(), help="ISO 8601 timestamp with timezone for the signature.")
    parser.add_argument("--force", action="store_true", help="Replace an existing bundle signature.")
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
    bundle_path = Path(args.bundle).resolve()
    if not bundle_path.exists():
        payload = {
            "result": "error",
            "bundle_path": str(bundle_path),
            "signer": args.signer,
            "key_id": args.key_id,
            "scheme": args.scheme,
            "public_key_fingerprint": "None",
            "signed_at": args.signed_at,
            "warnings": [],
            "errors": [f"Bundle does not exist: {bundle_path}"],
        }
        return emit(payload, args.format)

    try:
        bundle = load_bundle(bundle_path)
        if bundle.get("signature") and not args.force:
            raise ValueError("Bundle already has a signature. Pass --force to replace it.")
        secret = None
        public_key_fingerprint = "None"
        if args.scheme == "hmac-sha256":
            secret = resolve_signing_secret(secret_file=args.secret_file, secret_env=args.secret_env)
        else:
            if not args.private_key_file:
                raise ValueError("SSH bundle signing requires --private-key-file.")
            _, public_key_fingerprint = resolve_ssh_public_key(
                private_key_file=args.private_key_file,
                public_key_file=args.public_key_file,
            )
    except ValueError as exc:
        payload = {
            "result": "error",
            "bundle_path": str(bundle_path),
            "signer": args.signer,
            "key_id": args.key_id,
            "scheme": args.scheme,
            "public_key_fingerprint": "None",
            "signed_at": args.signed_at,
            "warnings": [],
            "errors": [str(exc)],
        }
        return emit(payload, args.format)

    signed_bundle = attach_bundle_signature(
        bundle=bundle,
        signer=args.signer,
        key_id=args.key_id,
        signed_at=args.signed_at,
        scheme=args.scheme,
        secret=secret,
        private_key_file=args.private_key_file,
        public_key_file=args.public_key_file,
    )
    signature = signed_bundle.get("signature") if isinstance(signed_bundle.get("signature"), dict) else {}
    bundle_path.write_text(json.dumps(signed_bundle, indent=2) + "\n", encoding="utf-8")
    payload = {
        "result": "signed",
        "bundle_path": str(bundle_path),
        "signer": args.signer,
        "key_id": args.key_id,
        "scheme": str(signature.get("scheme", args.scheme)),
        "public_key_fingerprint": str(signature.get("public_key_fingerprint", public_key_fingerprint)),
        "signed_at": args.signed_at,
        "warnings": [],
        "errors": [],
    }
    return emit(payload, args.format)


if __name__ == "__main__":
    raise SystemExit(main())
