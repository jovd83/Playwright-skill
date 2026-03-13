#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from handoff_bundle import load_bundle, verify_bundle_signature  # type: ignore
from inspect_handoff_bundle import build_bundle_payload  # type: ignore
from resolve_test_docs_root import resolve_docs_root  # type: ignore


DEFAULT_TRUST_POLICY_FILE_NAME = "handoff-bundle-trust-policy.json"
TRUST_POLICY_PROFILE_KEYS = {
    "allow_inspection_warnings",
    "allow_source_not_ready",
    "allow_active_lease",
    "allow_expired_lease",
    "max_age_hours",
    "allowed_updated_by",
    "allowed_next_owner",
    "require_signature",
    "allowed_signature_schemes",
    "allowed_signers",
    "allowed_key_ids",
    "allowed_public_key_fingerprints",
    "revoked_signers",
    "revoked_key_ids",
    "revoked_public_key_fingerprints",
    "signature_secret_env",
}


def build_trust_policy(
    allow_inspection_warnings: bool = False,
    allow_source_not_ready: bool = False,
    allow_active_lease: bool = False,
    allow_expired_lease: bool = False,
    max_age_hours: int | None = None,
    allowed_updated_by: list[str] | None = None,
    allowed_next_owner: list[str] | None = None,
    require_signature: bool = False,
    allowed_signature_schemes: list[str] | None = None,
    allowed_signers: list[str] | None = None,
    allowed_key_ids: list[str] | None = None,
    allowed_public_key_fingerprints: list[str] | None = None,
    revoked_signers: list[str] | None = None,
    revoked_key_ids: list[str] | None = None,
    revoked_public_key_fingerprints: list[str] | None = None,
    signature_secret_env: str | None = None,
) -> dict[str, Any]:
    allowed_source_readiness = ["ready", "ready-with-warnings"]
    if allow_source_not_ready:
        allowed_source_readiness.append("not-ready")

    allowed_lease_states = ["none"]
    if allow_active_lease:
        allowed_lease_states.append("active")
    if allow_expired_lease:
        allowed_lease_states.append("expired")

    return {
        "allow_inspection_warnings": allow_inspection_warnings,
        "allowed_source_readiness": allowed_source_readiness,
        "allowed_lease_states": allowed_lease_states,
        "max_age_hours": max_age_hours,
        "allowed_updated_by": allowed_updated_by or [],
        "allowed_next_owner": allowed_next_owner or [],
        "require_signature": require_signature,
        "allowed_signature_schemes": allowed_signature_schemes or [],
        "allowed_signers": allowed_signers or [],
        "allowed_key_ids": allowed_key_ids or [],
        "allowed_public_key_fingerprints": allowed_public_key_fingerprints or [],
        "revoked_signers": revoked_signers or [],
        "revoked_key_ids": revoked_key_ids or [],
        "revoked_public_key_fingerprints": revoked_public_key_fingerprints or [],
        "signature_secret_env": signature_secret_env,
    }


def default_trust_policy() -> dict[str, Any]:
    return build_trust_policy()


def append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def require_bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be true or false.")
    return value


def require_optional_int(value: object, label: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer or null.")
    return value


def require_string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array of non-empty strings.")
    normalized: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{label}[{index}] must be a non-empty string.")
        normalized.append(item.strip())
    return normalized


def require_optional_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string or null.")
    return value.strip()


def load_trust_policy_definition(policy_path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Trust policy file does not exist: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Trust policy file is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("Trust policy root must be a JSON object.")

    allowed_keys = {
        "allow_inspection_warnings",
        "allow_source_not_ready",
        "allow_active_lease",
        "allow_expired_lease",
        "max_age_hours",
        "allowed_updated_by",
        "allowed_next_owner",
        "require_signature",
        "allowed_signature_schemes",
        "allowed_signers",
        "allowed_key_ids",
        "allowed_public_key_fingerprints",
        "revoked_signers",
        "revoked_key_ids",
        "revoked_public_key_fingerprints",
        "signature_secret_env",
        "default_profile",
        "profiles",
    }
    unknown_keys = sorted(key for key in raw if key not in allowed_keys)
    if unknown_keys:
        raise ValueError(f"Trust policy file contains unknown keys: {', '.join(unknown_keys)}")

    policy = build_trust_policy(
        allow_inspection_warnings=require_bool(raw.get("allow_inspection_warnings", False), "allow_inspection_warnings"),
        allow_source_not_ready=require_bool(raw.get("allow_source_not_ready", False), "allow_source_not_ready"),
        allow_active_lease=require_bool(raw.get("allow_active_lease", False), "allow_active_lease"),
        allow_expired_lease=require_bool(raw.get("allow_expired_lease", False), "allow_expired_lease"),
        max_age_hours=require_optional_int(raw.get("max_age_hours"), "max_age_hours"),
        allowed_updated_by=require_string_list(raw.get("allowed_updated_by", []), "allowed_updated_by"),
        allowed_next_owner=require_string_list(raw.get("allowed_next_owner", []), "allowed_next_owner"),
        require_signature=require_bool(raw.get("require_signature", False), "require_signature"),
        allowed_signature_schemes=require_string_list(raw.get("allowed_signature_schemes", []), "allowed_signature_schemes"),
        allowed_signers=require_string_list(raw.get("allowed_signers", []), "allowed_signers"),
        allowed_key_ids=require_string_list(raw.get("allowed_key_ids", []), "allowed_key_ids"),
        allowed_public_key_fingerprints=require_string_list(raw.get("allowed_public_key_fingerprints", []), "allowed_public_key_fingerprints"),
        revoked_signers=require_string_list(raw.get("revoked_signers", []), "revoked_signers"),
        revoked_key_ids=require_string_list(raw.get("revoked_key_ids", []), "revoked_key_ids"),
        revoked_public_key_fingerprints=require_string_list(raw.get("revoked_public_key_fingerprints", []), "revoked_public_key_fingerprints"),
        signature_secret_env=require_optional_string(raw.get("signature_secret_env"), "signature_secret_env"),
    )
    default_profile = require_optional_string(raw.get("default_profile"), "default_profile")
    raw_profiles = raw.get("profiles", {})
    if not isinstance(raw_profiles, dict):
        raise ValueError("profiles must be a JSON object keyed by profile name.")
    profiles: dict[str, dict[str, Any]] = {}
    for profile_name, profile_value in raw_profiles.items():
        if not isinstance(profile_name, str) or not profile_name.strip():
            raise ValueError("profiles keys must be non-empty strings.")
        if not isinstance(profile_value, dict):
            raise ValueError(f"profiles.{profile_name} must be a JSON object.")
        profile_unknown_keys = sorted(key for key in profile_value if key not in TRUST_POLICY_PROFILE_KEYS)
        if profile_unknown_keys:
            raise ValueError(f"profiles.{profile_name} contains unknown keys: {', '.join(profile_unknown_keys)}")
        profiles[profile_name.strip()] = build_trust_policy(
            allow_inspection_warnings=require_bool(profile_value.get("allow_inspection_warnings", False), f"profiles.{profile_name}.allow_inspection_warnings"),
            allow_source_not_ready=require_bool(profile_value.get("allow_source_not_ready", False), f"profiles.{profile_name}.allow_source_not_ready"),
            allow_active_lease=require_bool(profile_value.get("allow_active_lease", False), f"profiles.{profile_name}.allow_active_lease"),
            allow_expired_lease=require_bool(profile_value.get("allow_expired_lease", False), f"profiles.{profile_name}.allow_expired_lease"),
            max_age_hours=require_optional_int(profile_value.get("max_age_hours"), f"profiles.{profile_name}.max_age_hours"),
            allowed_updated_by=require_string_list(profile_value.get("allowed_updated_by", []), f"profiles.{profile_name}.allowed_updated_by"),
            allowed_next_owner=require_string_list(profile_value.get("allowed_next_owner", []), f"profiles.{profile_name}.allowed_next_owner"),
            require_signature=require_bool(profile_value.get("require_signature", False), f"profiles.{profile_name}.require_signature"),
            allowed_signature_schemes=require_string_list(profile_value.get("allowed_signature_schemes", []), f"profiles.{profile_name}.allowed_signature_schemes"),
            allowed_signers=require_string_list(profile_value.get("allowed_signers", []), f"profiles.{profile_name}.allowed_signers"),
            allowed_key_ids=require_string_list(profile_value.get("allowed_key_ids", []), f"profiles.{profile_name}.allowed_key_ids"),
            allowed_public_key_fingerprints=require_string_list(profile_value.get("allowed_public_key_fingerprints", []), f"profiles.{profile_name}.allowed_public_key_fingerprints"),
            revoked_signers=require_string_list(profile_value.get("revoked_signers", []), f"profiles.{profile_name}.revoked_signers"),
            revoked_key_ids=require_string_list(profile_value.get("revoked_key_ids", []), f"profiles.{profile_name}.revoked_key_ids"),
            revoked_public_key_fingerprints=require_string_list(profile_value.get("revoked_public_key_fingerprints", []), f"profiles.{profile_name}.revoked_public_key_fingerprints"),
            signature_secret_env=require_optional_string(profile_value.get("signature_secret_env"), f"profiles.{profile_name}.signature_secret_env"),
        )
    if default_profile is not None and default_profile not in profiles:
        raise ValueError(f"default_profile {default_profile!r} is not defined in profiles.")
    policy["default_profile"] = default_profile
    policy["profiles"] = profiles
    return policy


def materialize_trust_policy(policy_definition: dict[str, Any], profile_name: str | None = None) -> dict[str, Any]:
    profiles = dict(policy_definition.get("profiles", {}))
    selected_profile = profile_name or policy_definition.get("default_profile")
    base_policy = {key: value for key, value in policy_definition.items() if key not in {"default_profile", "profiles"}}
    if selected_profile is None:
        return base_policy
    if selected_profile not in profiles:
        raise ValueError(f"Trust policy profile {selected_profile!r} is not defined.")
    profile_policy = profiles[selected_profile]
    merged_policy = dict(base_policy)
    for key, value in profile_policy.items():
        merged_policy[key] = value
    return merged_policy


def load_trust_policy_file(policy_path: Path, profile_name: str | None = None) -> dict[str, Any]:
    return materialize_trust_policy(load_trust_policy_definition(policy_path), profile_name)


def serialize_trust_policy_definition(policy_definition: dict[str, Any]) -> dict[str, Any]:
    serialized = {
        "allow_inspection_warnings": bool(policy_definition["allow_inspection_warnings"]),
        "allow_source_not_ready": "not-ready" in policy_definition["allowed_source_readiness"],
        "allow_active_lease": "active" in policy_definition["allowed_lease_states"],
        "allow_expired_lease": "expired" in policy_definition["allowed_lease_states"],
        "max_age_hours": policy_definition["max_age_hours"],
        "allowed_updated_by": list(policy_definition["allowed_updated_by"]),
        "allowed_next_owner": list(policy_definition["allowed_next_owner"]),
        "require_signature": bool(policy_definition["require_signature"]),
        "allowed_signature_schemes": list(policy_definition["allowed_signature_schemes"]),
        "allowed_signers": list(policy_definition["allowed_signers"]),
        "allowed_key_ids": list(policy_definition["allowed_key_ids"]),
        "allowed_public_key_fingerprints": list(policy_definition["allowed_public_key_fingerprints"]),
        "revoked_signers": list(policy_definition["revoked_signers"]),
        "revoked_key_ids": list(policy_definition["revoked_key_ids"]),
        "revoked_public_key_fingerprints": list(policy_definition["revoked_public_key_fingerprints"]),
        "signature_secret_env": policy_definition["signature_secret_env"],
    }
    default_profile = policy_definition.get("default_profile")
    profiles = dict(policy_definition.get("profiles", {}))
    if default_profile is not None:
        serialized["default_profile"] = default_profile
    if profiles:
        serialized["profiles"] = {
            profile_name: serialize_trust_policy_definition(profile_policy)
            for profile_name, profile_policy in profiles.items()
        }
    return serialized


def resolve_trust_policy_path(
    start_dir: Path,
    explicit_root: str | None = None,
    explicit_policy_path: str | None = None,
    use_default_policy_file: bool = True,
) -> Path | None:
    if explicit_policy_path:
        return Path(explicit_policy_path).resolve()
    if not use_default_policy_file:
        return None
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=explicit_root)
    candidate = (docs_root / DEFAULT_TRUST_POLICY_FILE_NAME).resolve()
    if candidate.exists():
        return candidate
    return None


def merge_trust_policy(
    base_policy: dict[str, Any],
    *,
    allow_inspection_warnings: bool = False,
    allow_source_not_ready: bool = False,
    allow_active_lease: bool = False,
    allow_expired_lease: bool = False,
    max_age_hours: int | None = None,
    allowed_updated_by: list[str] | None = None,
    allowed_next_owner: list[str] | None = None,
    require_signature: bool = False,
    allowed_signature_schemes: list[str] | None = None,
    allowed_signers: list[str] | None = None,
    allowed_key_ids: list[str] | None = None,
    allowed_public_key_fingerprints: list[str] | None = None,
    revoked_signers: list[str] | None = None,
    revoked_key_ids: list[str] | None = None,
    revoked_public_key_fingerprints: list[str] | None = None,
    signature_secret_env: str | None = None,
) -> dict[str, Any]:
    policy = dict(base_policy)
    if allow_inspection_warnings:
        policy["allow_inspection_warnings"] = True
    if allow_source_not_ready:
        allowed_source_readiness = list(policy["allowed_source_readiness"])
        if "not-ready" not in allowed_source_readiness:
            allowed_source_readiness.append("not-ready")
        policy["allowed_source_readiness"] = allowed_source_readiness
    if allow_active_lease:
        allowed_lease_states = list(policy["allowed_lease_states"])
        if "active" not in allowed_lease_states:
            allowed_lease_states.append("active")
        policy["allowed_lease_states"] = allowed_lease_states
    if allow_expired_lease:
        allowed_lease_states = list(policy["allowed_lease_states"])
        if "expired" not in allowed_lease_states:
            allowed_lease_states.append("expired")
        policy["allowed_lease_states"] = allowed_lease_states
    if max_age_hours is not None:
        policy["max_age_hours"] = max_age_hours
    if allowed_updated_by is not None:
        policy["allowed_updated_by"] = allowed_updated_by
    if allowed_next_owner is not None:
        policy["allowed_next_owner"] = allowed_next_owner
    if require_signature:
        policy["require_signature"] = True
    if allowed_signature_schemes is not None:
        policy["allowed_signature_schemes"] = allowed_signature_schemes
    if allowed_signers is not None:
        policy["allowed_signers"] = allowed_signers
    if allowed_key_ids is not None:
        policy["allowed_key_ids"] = allowed_key_ids
    if allowed_public_key_fingerprints is not None:
        policy["allowed_public_key_fingerprints"] = allowed_public_key_fingerprints
    if revoked_signers is not None:
        policy["revoked_signers"] = revoked_signers
    if revoked_key_ids is not None:
        policy["revoked_key_ids"] = revoked_key_ids
    if revoked_public_key_fingerprints is not None:
        policy["revoked_public_key_fingerprints"] = revoked_public_key_fingerprints
    if signature_secret_env is not None:
        policy["signature_secret_env"] = signature_secret_env
    return policy


def build_trust_payload(
    bundle_path: Path,
    policy: dict[str, Any],
    verification_secret: str | None = None,
    policy_source: str = "default",
) -> dict[str, object]:
    try:
        inspection = build_bundle_payload(bundle_path)
    except (FileNotFoundError, ValueError) as exc:
        return {
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
            "policy": policy,
            "signature_present": False,
            "signature_scheme": "unknown",
            "signature_signer": "unknown",
            "signature_key_id": "unknown",
            "signature_public_key_fingerprint": "unknown",
            "signature_verified": False,
            "warnings": [],
            "blocking_reasons": [str(exc)],
            "next_actions": [
                "Run python ../shared/scripts/inspect_handoff_bundle.py --bundle <handoff-bundle.json> --format text and fix the reported bundle errors."
            ],
            "inspection": None,
        }

    blocking_reasons: list[str] = []
    warnings: list[str] = list(inspection["warnings"])
    next_actions: list[str] = []

    if inspection["errors"]:
        blocking_reasons.extend(inspection["errors"])
        append_unique(next_actions, "Run python ../shared/scripts/inspect_handoff_bundle.py --bundle <handoff-bundle.json> --format text and fix the reported bundle errors.")

    if inspection["result"] == "valid-with-warnings" and not policy["allow_inspection_warnings"]:
        blocking_reasons.append("Bundle inspection reported warnings and the trust policy does not allow them.")
        append_unique(next_actions, "Resolve the inspection warnings or pass a relaxed trust policy.")

    source_readiness_verdict = str(inspection["source_readiness_verdict"])
    if source_readiness_verdict not in policy["allowed_source_readiness"]:
        blocking_reasons.append(
            f"Bundle source readiness verdict {source_readiness_verdict!r} is not allowed by the trust policy."
        )
        append_unique(next_actions, "Re-export after end-session or use a trust policy that explicitly allows active work bundles.")

    lease_state = str(inspection["lease_state"])
    if lease_state not in policy["allowed_lease_states"]:
        blocking_reasons.append(f"Bundle lease state {lease_state!r} is not allowed by the trust policy.")
        if lease_state == "active":
            append_unique(next_actions, "Release the lease with end_handoff_session.py or manage_handoff_lease.py before exporting a transfer-ready bundle.")
        elif lease_state == "expired":
            append_unique(next_actions, "Refresh the workspace state and export a bundle with a current lease decision.")

    allowed_updated_by = policy["allowed_updated_by"]
    if allowed_updated_by and str(inspection["updated_by"]) not in allowed_updated_by:
        blocking_reasons.append(
            f"Bundle Updated by {inspection['updated_by']!r} is not allowed by the trust policy."
        )
        append_unique(next_actions, "Re-export from an allowed operator or relax the allowed Updated by list.")

    allowed_next_owner = policy["allowed_next_owner"]
    if allowed_next_owner and str(inspection["next_owner"]) not in allowed_next_owner:
        blocking_reasons.append(
            f"Bundle Next owner {inspection['next_owner']!r} is not allowed by the trust policy."
        )
        append_unique(next_actions, "Re-export with an allowed next owner or relax the allowed Next owner list.")

    signature_present = bool(inspection["signature_present"])
    signature_scheme = str(inspection["signature_scheme"])
    signature_signer = str(inspection["signature_signer"])
    signature_key_id = str(inspection["signature_key_id"])
    signature_public_key_fingerprint = str(inspection.get("signature_public_key_fingerprint", "None"))
    require_signature = bool(policy["require_signature"])
    allowed_signature_schemes = list(policy["allowed_signature_schemes"])
    allowed_signers = list(policy["allowed_signers"])
    allowed_key_ids = list(policy["allowed_key_ids"])
    allowed_public_key_fingerprints = list(policy["allowed_public_key_fingerprints"])
    revoked_signers = list(policy["revoked_signers"])
    revoked_key_ids = list(policy["revoked_key_ids"])
    revoked_public_key_fingerprints = list(policy["revoked_public_key_fingerprints"])
    signature_constraints = (
        require_signature
        or bool(allowed_signature_schemes)
        or bool(allowed_signers)
        or bool(allowed_key_ids)
        or bool(allowed_public_key_fingerprints)
        or bool(revoked_signers)
        or bool(revoked_key_ids)
        or bool(revoked_public_key_fingerprints)
    )

    if require_signature and not signature_present:
        blocking_reasons.append("Bundle signature is required by the trust policy, but the bundle is unsigned.")
        append_unique(next_actions, "Run python ../shared/scripts/sign_handoff_bundle.py --bundle <handoff-bundle.json> --signer <actor> --key-id <key-id>.")

    if allowed_signature_schemes and signature_scheme not in allowed_signature_schemes:
        blocking_reasons.append(
            f"Bundle signature scheme {signature_scheme!r} is not allowed by the trust policy."
        )
        append_unique(next_actions, "Re-sign the bundle with an allowed signature scheme or relax the allowed scheme list.")

    if allowed_signers and signature_signer not in allowed_signers:
        blocking_reasons.append(
            f"Bundle signature signer {signature_signer!r} is not allowed by the trust policy."
        )
        append_unique(next_actions, "Re-sign the bundle with an allowed signer or relax the allowed signer list.")

    if allowed_key_ids and signature_key_id not in allowed_key_ids:
        blocking_reasons.append(
            f"Bundle signature key id {signature_key_id!r} is not allowed by the trust policy."
        )
        append_unique(next_actions, "Re-sign the bundle with an allowed key id or relax the allowed key id list.")

    if allowed_public_key_fingerprints and signature_public_key_fingerprint not in allowed_public_key_fingerprints:
        blocking_reasons.append(
            f"Bundle signature public key fingerprint {signature_public_key_fingerprint!r} is not allowed by the trust policy."
        )
        append_unique(next_actions, "Re-sign the bundle with an allowed signing key or relax the allowed public key fingerprint list.")

    if signature_present and revoked_signers and signature_signer in revoked_signers:
        blocking_reasons.append(
            f"Bundle signature signer {signature_signer!r} has been revoked by the trust policy."
        )
        append_unique(next_actions, "Re-sign the bundle with a non-revoked signer and update any stale trust policy references.")

    if signature_present and revoked_key_ids and signature_key_id in revoked_key_ids:
        blocking_reasons.append(
            f"Bundle signature key id {signature_key_id!r} has been revoked by the trust policy."
        )
        append_unique(next_actions, "Re-sign the bundle with a non-revoked key id and rotate the checked-in policy if needed.")

    if signature_present and revoked_public_key_fingerprints and signature_public_key_fingerprint in revoked_public_key_fingerprints:
        blocking_reasons.append(
            f"Bundle signature public key fingerprint {signature_public_key_fingerprint!r} has been revoked by the trust policy."
        )
        append_unique(next_actions, "Re-sign the bundle with a non-revoked signing key and rotate the checked-in policy if needed.")

    signature_verified = False
    signature_errors: list[str] = []
    if signature_constraints:
        if signature_present and signature_scheme == "hmac-sha256" and verification_secret is None:
            blocking_reasons.append(
                "Trust policy requires signature verification, but no verification secret was provided."
            )
            append_unique(
                next_actions,
                "Pass --secret-file <path> or set HANDOFF_BUNDLE_SIGNING_SECRET before applying signature trust checks.",
            )
        elif signature_present:
            try:
                bundle = load_bundle(bundle_path)
            except ValueError as exc:
                signature_errors.append(str(exc))
            else:
                signature_errors.extend(
                    verify_bundle_signature(
                        bundle,
                        verification_secret,
                        required_scheme=None,
                        required_public_key_fingerprint=None,
                    )
                )
            if signature_errors:
                blocking_reasons.extend(f"SIGNATURE: {error}" for error in signature_errors)
                append_unique(
                    next_actions,
                    "Run python ../shared/scripts/verify_handoff_bundle_signature.py --bundle <handoff-bundle.json> and fix the reported signature errors.",
                )
            else:
                signature_verified = True

    max_age_hours = policy["max_age_hours"]
    if max_age_hours is not None:
        try:
            exported_at = datetime.fromisoformat(str(inspection["exported_at"]))
        except ValueError:
            blocking_reasons.append(f"Bundle exported_at timestamp is invalid: {inspection['exported_at']!r}.")
            append_unique(next_actions, "Re-export the bundle so the timestamp is regenerated.")
        else:
            if exported_at.tzinfo is None or exported_at.utcoffset() is None:
                blocking_reasons.append("Bundle exported_at timestamp is missing a timezone offset.")
                append_unique(next_actions, "Re-export the bundle so the timestamp includes a timezone offset.")
            else:
                age_hours = (datetime.now().astimezone() - exported_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    blocking_reasons.append(
                        f"Bundle is older than the trust policy allows: {age_hours:.2f}h > {max_age_hours}h."
                    )
                    append_unique(next_actions, "Re-export a fresh bundle or raise the maximum allowed age.")

    result = "trusted"
    if warnings:
        result = "trusted-with-warnings"
    if blocking_reasons:
        result = "untrusted"

    return {
        "result": result,
        "bundle_path": str(bundle_path),
        "task": inspection["task"],
        "status": inspection["status"],
        "updated_by": inspection["updated_by"],
        "next_owner": inspection["next_owner"],
        "exported_at": inspection["exported_at"],
        "lease_state": inspection["lease_state"],
        "source_readiness_verdict": inspection["source_readiness_verdict"],
        "policy_source": policy_source,
        "signature_present": signature_present,
        "signature_scheme": signature_scheme,
        "signature_signer": signature_signer,
        "signature_key_id": signature_key_id,
        "signature_public_key_fingerprint": signature_public_key_fingerprint,
        "signature_verified": signature_verified,
        "policy": policy,
        "warnings": warnings,
        "blocking_reasons": blocking_reasons,
        "next_actions": next_actions,
        "inspection": inspection,
    }
