#!/usr/bin/env python3
from __future__ import annotations

import base64
import hmac
import hashlib
import json
from datetime import datetime
from pathlib import Path
import os
import subprocess
import sys
import tempfile
from typing import Any


BUNDLE_ROOT = Path(__file__).resolve().parents[3]
HANDOVER_SCRIPTS = BUNDLE_ROOT / "documentation" / "handover" / "scripts"
SESSION_SCRIPTS = BUNDLE_ROOT / "documentation" / "session-state" / "scripts"

for script_dir in (HANDOVER_SCRIPTS, SESSION_SCRIPTS):
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    parse_sections as parse_handover_sections,
)
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    parse_sections as parse_session_sections,
)


BUNDLE_VERSION = 2
SSH_SIGNATURE_NAMESPACE = "handoff-bundle"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def json_sha256(value: Any) -> str:
    return text_sha256(canonical_json(value))


def bundle_payload_for_integrity(bundle: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in bundle.items() if key not in {"integrity", "signature"}}


def bundle_payload_for_signature(bundle: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in bundle.items() if key != "signature"}


def build_bundle_integrity(bundle_without_integrity: dict[str, Any]) -> dict[str, str]:
    documents = bundle_without_integrity["documents"]
    lease = bundle_without_integrity["lease"]
    return {
        "source_sha256": json_sha256(bundle_without_integrity["source"]),
        "handover_markdown_sha256": text_sha256(documents["handover_markdown"]),
        "session_state_markdown_sha256": text_sha256(documents["session_state_markdown"]),
        "lease_payload_sha256": json_sha256(lease["payload"]),
        "lease_inspection_sha256": json_sha256(lease["inspection"]),
        "report_sha256": json_sha256(bundle_without_integrity["report"]),
        "readiness_sha256": json_sha256(bundle_without_integrity["readiness"]),
        "bundle_sha256": json_sha256(bundle_without_integrity),
    }


def attach_bundle_integrity(bundle_without_integrity: dict[str, Any]) -> dict[str, Any]:
    bundle = dict(bundle_without_integrity)
    bundle["integrity"] = build_bundle_integrity(bundle_without_integrity)
    return bundle


def verify_bundle_integrity(bundle: dict[str, Any]) -> list[str]:
    integrity = bundle.get("integrity")
    if not isinstance(integrity, dict):
        return ["Bundle integrity metadata is missing or invalid."]

    expected = build_bundle_integrity(bundle_payload_for_integrity(bundle))
    labels = {
        "source_sha256": "source content hash",
        "handover_markdown_sha256": "handover markdown hash",
        "session_state_markdown_sha256": "session-state markdown hash",
        "lease_payload_sha256": "lease payload hash",
        "lease_inspection_sha256": "lease inspection hash",
        "report_sha256": "report hash",
        "readiness_sha256": "readiness hash",
        "bundle_sha256": "bundle hash",
    }

    errors: list[str] = []
    for key, expected_value in expected.items():
        actual_value = integrity.get(key)
        if not isinstance(actual_value, str) or not actual_value.strip():
            errors.append(f"Bundle integrity metadata is missing {key}.")
            continue
        if actual_value != expected_value:
            errors.append(f"Bundle {labels[key]} does not match integrity metadata.")
    return errors


def resolve_signing_secret(secret_file: str | None = None, secret_env: str = "HANDOFF_BUNDLE_SIGNING_SECRET") -> str:
    if secret_file:
        secret = Path(secret_file).read_text(encoding="utf-8").strip()
        if not secret:
            raise ValueError(f"Signing secret file is empty: {secret_file}")
        return secret

    secret = os.environ.get(secret_env, "").strip()
    if not secret:
        raise ValueError(f"Signing secret was not found in environment variable {secret_env}.")
    return secret


def hmac_sha256(value: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()


def run_command(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    return result


def require_file_exists(path: Path, label: str) -> Path:
    if not path.exists():
        raise ValueError(f"{label} does not exist: {path}")
    return path


def normalize_public_key(public_key: str) -> str:
    value = public_key.strip()
    if not value:
        raise ValueError("SSH public key content is empty.")
    return value


def public_key_algorithm(public_key: str) -> str:
    return normalize_public_key(public_key).split()[0]


def ssh_public_key_fingerprint(public_key: str) -> str:
    normalized_key = normalize_public_key(public_key)
    with tempfile.TemporaryDirectory(prefix="handoff-bundle-key-") as tmp_dir_name:
        temp_key = Path(tmp_dir_name) / "bundle_signing_key.pub"
        temp_key.write_text(normalized_key + "\n", encoding="utf-8")
        result = run_command(["ssh-keygen", "-l", "-f", str(temp_key)])
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or result.stdout.strip() or "ssh-keygen failed while fingerprinting the public key.")
    parts = result.stdout.strip().split()
    if len(parts) < 2:
        raise ValueError(f"Could not parse SSH public key fingerprint from ssh-keygen output: {result.stdout!r}")
    return parts[1]


def resolve_ssh_public_key(
    private_key_file: str | None = None,
    public_key_file: str | None = None,
) -> tuple[str, str]:
    if public_key_file:
        public_key_path = require_file_exists(Path(public_key_file).resolve(), "SSH public key file")
    elif private_key_file:
        public_key_path = require_file_exists(Path(f"{Path(private_key_file).resolve()}.pub"), "Inferred SSH public key file")
    else:
        raise ValueError("SSH signatures require --private-key-file and a matching public key.")
    public_key = normalize_public_key(public_key_path.read_text(encoding="utf-8"))
    return public_key, ssh_public_key_fingerprint(public_key)


def build_ssh_signature_blob(payload: str, private_key_file: str, public_key: str) -> tuple[str, str, str]:
    private_key_path = require_file_exists(Path(private_key_file).resolve(), "SSH private key file")
    with tempfile.TemporaryDirectory(prefix="handoff-bundle-sign-") as tmp_dir_name:
        payload_path = Path(tmp_dir_name) / "payload.json"
        payload_path.write_text(payload, encoding="utf-8")
        result = run_command(
            [
                "ssh-keygen",
                "-Y",
                "sign",
                "-f",
                str(private_key_path),
                "-n",
                SSH_SIGNATURE_NAMESPACE,
                str(payload_path),
            ]
        )
        if result.returncode != 0:
            raise ValueError(result.stderr.strip() or result.stdout.strip() or "ssh-keygen failed while signing the bundle.")
        signature_path = Path(f"{payload_path}.sig")
        signature_blob = signature_path.read_text(encoding="utf-8").strip()
    return signature_blob, public_key_algorithm(public_key), ssh_public_key_fingerprint(public_key)


def verify_ssh_signature_blob(
    payload: str,
    *,
    signature_blob: str,
    signer: str,
    public_key: str,
    namespace: str,
) -> list[str]:
    normalized_public_key = normalize_public_key(public_key)
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="handoff-bundle-verify-") as tmp_dir_name:
        temp_root = Path(tmp_dir_name)
        allowed_signers = temp_root / "allowed_signers"
        signature_path = temp_root / "bundle.sig"
        allowed_signers.write_text(
            f'{signer} namespaces="{namespace}" {normalized_public_key}\n',
            encoding="utf-8",
        )
        signature_path.write_text(signature_blob.strip() + "\n", encoding="utf-8")
        result = run_command(
            [
                "ssh-keygen",
                "-Y",
                "verify",
                "-f",
                str(allowed_signers),
                "-I",
                signer,
                "-n",
                namespace,
                "-s",
                str(signature_path),
            ],
            input_text=payload,
        )
    if result.returncode != 0:
        errors.append(result.stderr.strip() or result.stdout.strip() or "ssh-keygen failed while verifying the bundle signature.")
    return errors


def build_bundle_signature(
    bundle_without_signature: dict[str, Any],
    signer: str,
    key_id: str,
    signed_at: str,
    *,
    scheme: str = "hmac-sha256",
    secret: str | None = None,
    private_key_file: str | None = None,
    public_key_file: str | None = None,
) -> dict[str, str]:
    payload = canonical_json(bundle_without_signature)
    if scheme == "hmac-sha256":
        if secret is None:
            raise ValueError("HMAC bundle signatures require a signing secret.")
        return {
            "scheme": "hmac-sha256",
            "signer": signer,
            "key_id": key_id,
            "signed_at": signed_at,
            "digest": hmac_sha256(payload, secret),
        }
    if scheme == "sshsig":
        if private_key_file is None:
            raise ValueError("SSH bundle signatures require a private key file.")
        public_key, public_key_fingerprint = resolve_ssh_public_key(private_key_file=private_key_file, public_key_file=public_key_file)
        signature_blob, public_key_type, verified_fingerprint = build_ssh_signature_blob(payload, private_key_file, public_key)
        return {
            "scheme": "sshsig",
            "signer": signer,
            "key_id": key_id,
            "signed_at": signed_at,
            "namespace": SSH_SIGNATURE_NAMESPACE,
            "public_key": public_key,
            "public_key_type": public_key_type,
            "public_key_fingerprint": verified_fingerprint or public_key_fingerprint,
            "signature_blob_base64": base64.b64encode(signature_blob.encode("utf-8")).decode("ascii"),
        }
    raise ValueError(f"Unsupported bundle signature scheme: {scheme!r}")


def attach_bundle_signature(
    bundle: dict[str, Any],
    signer: str,
    key_id: str,
    signed_at: str,
    *,
    scheme: str = "hmac-sha256",
    secret: str | None = None,
    private_key_file: str | None = None,
    public_key_file: str | None = None,
) -> dict[str, Any]:
    bundle_without_signature = bundle_payload_for_signature(bundle)
    signed_bundle = dict(bundle_without_signature)
    signed_bundle["signature"] = build_bundle_signature(
        bundle_without_signature=bundle_without_signature,
        signer=signer,
        key_id=key_id,
        signed_at=signed_at,
        scheme=scheme,
        secret=secret,
        private_key_file=private_key_file,
        public_key_file=public_key_file,
    )
    return signed_bundle


def verify_bundle_signature(
    bundle: dict[str, Any],
    secret: str | None = None,
    required_signer: str | None = None,
    required_key_id: str | None = None,
    required_scheme: str | None = None,
    required_public_key_fingerprint: str | None = None,
) -> list[str]:
    signature = bundle.get("signature")
    if not isinstance(signature, dict):
        return ["Bundle signature metadata is missing or invalid."]

    scheme = str(signature.get("scheme", "")).strip()
    signer = str(signature.get("signer", "")).strip()
    key_id = str(signature.get("key_id", "")).strip()
    signed_at = str(signature.get("signed_at", "")).strip()
    digest = str(signature.get("digest", "")).strip()

    errors: list[str] = []
    if scheme not in {"hmac-sha256", "sshsig"}:
        errors.append("Bundle signature scheme must be 'hmac-sha256' or 'sshsig'.")
    if not signer:
        errors.append("Bundle signature signer is required.")
    if not key_id:
        errors.append("Bundle signature key_id is required.")
    if not signed_at:
        errors.append("Bundle signature signed_at is required.")
    if required_scheme is not None and scheme != required_scheme:
        errors.append(f"Bundle signature scheme {scheme!r} does not match required scheme {required_scheme!r}.")
    if scheme == "hmac-sha256" and not digest:
        errors.append("Bundle signature digest is required.")
    if scheme == "sshsig":
        namespace = str(signature.get("namespace", "")).strip()
        public_key = str(signature.get("public_key", "")).strip()
        public_key_type = str(signature.get("public_key_type", "")).strip()
        public_key_fingerprint = str(signature.get("public_key_fingerprint", "")).strip()
        signature_blob_base64 = str(signature.get("signature_blob_base64", "")).strip()
        if namespace != SSH_SIGNATURE_NAMESPACE:
            errors.append(f"Bundle SSH signature namespace must be {SSH_SIGNATURE_NAMESPACE!r}.")
        if not public_key:
            errors.append("Bundle SSH signature public_key is required.")
        if not public_key_type:
            errors.append("Bundle SSH signature public_key_type is required.")
        if not public_key_fingerprint:
            errors.append("Bundle SSH signature public_key_fingerprint is required.")
        if not signature_blob_base64:
            errors.append("Bundle SSH signature signature_blob_base64 is required.")
        elif public_key:
            try:
                actual_public_key_fingerprint = ssh_public_key_fingerprint(public_key)
            except ValueError as exc:
                errors.append(str(exc))
            else:
                if public_key_fingerprint and public_key_fingerprint != actual_public_key_fingerprint:
                    errors.append("Bundle SSH signature public_key_fingerprint does not match the embedded public key.")
        if required_public_key_fingerprint is not None and public_key_fingerprint != required_public_key_fingerprint:
            errors.append(
                "Bundle signature public key fingerprint "
                f"{public_key_fingerprint!r} does not match required fingerprint {required_public_key_fingerprint!r}."
            )
    if signed_at:
        try:
            signed_at_value = datetime.fromisoformat(signed_at)
        except ValueError:
            errors.append(f"Bundle signature signed_at timestamp is invalid: {signed_at!r}.")
        else:
            if signed_at_value.tzinfo is None or signed_at_value.utcoffset() is None:
                errors.append("Bundle signature signed_at timestamp must include a timezone offset.")

    if required_signer is not None and signer != required_signer:
        errors.append(f"Bundle signature signer {signer!r} does not match required signer {required_signer!r}.")
    if required_key_id is not None and key_id != required_key_id:
        errors.append(f"Bundle signature key_id {key_id!r} does not match required key_id {required_key_id!r}.")
    if errors:
        return errors

    bundle_without_signature = bundle_payload_for_signature(bundle)
    payload = canonical_json(bundle_without_signature)
    if scheme == "hmac-sha256":
        if secret is None:
            errors.append("Bundle signature uses hmac-sha256, but no verification secret was provided.")
            return errors
        expected_digest = hmac_sha256(payload, secret)
        if not hmac.compare_digest(digest, expected_digest):
            errors.append("Bundle signature digest does not match the provided signing secret.")
        return errors

    signature_blob_base64 = str(signature.get("signature_blob_base64", "")).strip()
    public_key = str(signature.get("public_key", "")).strip()
    namespace = str(signature.get("namespace", "")).strip() or SSH_SIGNATURE_NAMESPACE
    try:
        signature_blob = base64.b64decode(signature_blob_base64.encode("ascii")).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        errors.append(f"Bundle SSH signature_blob_base64 is not valid UTF-8 base64 data: {exc}")
        return errors
    errors.extend(
        verify_ssh_signature_blob(
            payload,
            signature_blob=signature_blob,
            signer=signer,
            public_key=public_key,
            namespace=namespace,
        )
    )
    return errors


def require_mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return value


def require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    return value


def load_bundle(bundle_path: Path) -> dict[str, object]:
    try:
        raw = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Bundle is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("Bundle root must be a JSON object.")
    if raw.get("bundle_version") != BUNDLE_VERSION:
        raise ValueError(f"Bundle version must be {BUNDLE_VERSION}.")

    integrity_errors = verify_bundle_integrity(raw)
    if integrity_errors:
        raise ValueError("; ".join(integrity_errors))

    source = require_mapping(raw.get("source"), "Bundle source")
    documents = require_mapping(raw.get("documents"), "Bundle documents")
    lease = require_mapping(raw.get("lease"), "Bundle lease")

    source["handover_name"] = require_string(source.get("handover_name"), "Bundle source handover_name")
    source["session_state_name"] = require_string(source.get("session_state_name"), "Bundle source session_state_name")
    documents["handover_markdown"] = require_string(documents.get("handover_markdown"), "Bundle handover_markdown")
    documents["session_state_markdown"] = require_string(documents.get("session_state_markdown"), "Bundle session_state_markdown")

    payload = lease.get("payload")
    if payload is not None and not isinstance(payload, dict):
        raise ValueError("Bundle lease payload must be a JSON object or null.")

    return raw


def validate_bundle_documents(bundle: dict[str, object]) -> tuple[dict[str, str], dict[str, str]]:
    documents = require_mapping(bundle["documents"], "Bundle documents")
    handover_markdown = documents["handover_markdown"]
    session_markdown = documents["session_state_markdown"]

    handover_root, handover_sections, _ = parse_handover_sections(handover_markdown)
    if handover_root != HANDOVER_ROOT:
        raise ValueError(f"Bundle handover markdown has the wrong root heading: {handover_root!r}")

    session_root, session_sections, _ = parse_session_sections(session_markdown)
    if session_root != SESSION_ROOT:
        raise ValueError(f"Bundle session-state markdown has the wrong root heading: {session_root!r}")

    return handover_sections, session_sections
