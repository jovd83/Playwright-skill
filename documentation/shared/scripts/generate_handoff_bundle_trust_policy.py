#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from handoff_bundle_trust import (  # type: ignore
    DEFAULT_TRUST_POLICY_FILE_NAME,
    build_trust_policy,
)
from resolve_test_docs_root import resolve_docs_root  # type: ignore


PROFILE_PRESETS: dict[str, dict[str, object]] = {
    "dev": {
        "allow_inspection_warnings": True,
        "allow_source_not_ready": True,
        "allow_active_lease": True,
        "allow_expired_lease": True,
        "max_age_hours": None,
        "require_signature": False,
        "allowed_signature_schemes": [],
    },
    "staging": {
        "allow_inspection_warnings": False,
        "allow_source_not_ready": False,
        "allow_active_lease": False,
        "allow_expired_lease": True,
        "max_age_hours": 48,
        "require_signature": True,
        "allowed_signature_schemes": ["sshsig"],
    },
    "prod": {
        "allow_inspection_warnings": False,
        "allow_source_not_ready": False,
        "allow_active_lease": False,
        "allow_expired_lease": False,
        "max_age_hours": 24,
        "require_signature": True,
        "allowed_signature_schemes": ["sshsig"],
    },
}


def infer_profile_template(profile_name: str) -> str | None:
    normalized = profile_name.strip().lower().replace("_", "-")
    if normalized in PROFILE_PRESETS:
        return normalized
    return None


def parse_profile_mapping(raw_value: str, option_name: str) -> tuple[str, str]:
    if "=" not in raw_value:
        raise ValueError(f"{option_name} must look like PROFILE=VALUE: {raw_value!r}")
    profile_name, value = raw_value.split("=", 1)
    profile_name = profile_name.strip()
    value = value.strip()
    if not profile_name:
        raise ValueError(f"{option_name} must include a profile name: {raw_value!r}")
    if not value:
        raise ValueError(f"{option_name} must include a value: {raw_value!r}")
    return profile_name, value


def parse_profile_bool_mappings(entries: list[str] | None, option_name: str, declared_profiles: set[str]) -> dict[str, bool]:
    values: dict[str, bool] = {}
    for entry in entries or []:
        profile_name, raw_value = parse_profile_mapping(entry, option_name)
        if profile_name not in declared_profiles:
            raise ValueError(f"{option_name} references undeclared profile {profile_name!r}. Declare it via --profile-name first.")
        normalized = raw_value.lower()
        if normalized not in {"true", "false"}:
            raise ValueError(f"{option_name} must use true or false: {entry!r}")
        values[profile_name] = normalized == "true"
    return values


def parse_profile_int_mappings(entries: list[str] | None, option_name: str, declared_profiles: set[str]) -> dict[str, int]:
    values: dict[str, int] = {}
    for entry in entries or []:
        profile_name, raw_value = parse_profile_mapping(entry, option_name)
        if profile_name not in declared_profiles:
            raise ValueError(f"{option_name} references undeclared profile {profile_name!r}. Declare it via --profile-name first.")
        try:
            values[profile_name] = int(raw_value)
        except ValueError as exc:
            raise ValueError(f"{option_name} must use integer values: {entry!r}") from exc
    return values


def parse_profile_list_mappings(entries: list[str] | None, option_name: str, declared_profiles: set[str]) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for entry in entries or []:
        profile_name, raw_value = parse_profile_mapping(entry, option_name)
        if profile_name not in declared_profiles:
            raise ValueError(f"{option_name} references undeclared profile {profile_name!r}. Declare it via --profile-name first.")
        values.setdefault(profile_name, []).append(raw_value)
    return values


def parse_profile_string_mappings(entries: list[str] | None, option_name: str, declared_profiles: set[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for entry in entries or []:
        profile_name, raw_value = parse_profile_mapping(entry, option_name)
        if profile_name not in declared_profiles:
            raise ValueError(f"{option_name} references undeclared profile {profile_name!r}. Declare it via --profile-name first.")
        values[profile_name] = raw_value
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic handoff bundle trust policy JSON file."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--output", help=f"Explicit policy output path. Defaults to <docs-root>/{DEFAULT_TRUST_POLICY_FILE_NAME}.")
    parser.add_argument("--force", action="store_true", help="Overwrite the policy file if it already exists.")
    parser.add_argument("--allow-inspection-warnings", action="store_true", help="Allow bundles that inspect as valid-with-warnings.")
    parser.add_argument("--allow-source-not-ready", action="store_true", help="Allow bundles exported from active not-ready workspaces.")
    parser.add_argument("--allow-active-lease", action="store_true", help="Allow bundles that carry an active lease.")
    parser.add_argument("--allow-expired-lease", action="store_true", help="Allow bundles that carry an expired lease.")
    parser.add_argument("--max-age-hours", type=int, help="Maximum allowed bundle age in hours.")
    parser.add_argument("--allowed-updated-by", action="append", help="Repeat to allow only specific Updated by values.")
    parser.add_argument("--allowed-next-owner", action="append", help="Repeat to allow only specific Next owner values.")
    parser.add_argument("--require-signature", action="store_true", help="Require signed bundles.")
    parser.add_argument("--allowed-signature-scheme", action="append", help="Repeat to allow only specific signature schemes.")
    parser.add_argument("--allowed-signer", action="append", help="Repeat to allow only specific signature signer values.")
    parser.add_argument("--allowed-key-id", action="append", help="Repeat to allow only specific signature key id values.")
    parser.add_argument("--allowed-public-key-fingerprint", action="append", help="Repeat to allow only specific SSH public key fingerprints.")
    parser.add_argument("--revoked-signer", action="append", help="Repeat to block specific revoked signature signer values.")
    parser.add_argument("--revoked-key-id", action="append", help="Repeat to block specific revoked signature key id values.")
    parser.add_argument("--revoked-public-key-fingerprint", action="append", help="Repeat to block specific revoked SSH public key fingerprints.")
    parser.add_argument("--profile-name", action="append", help="Repeat to scaffold named trust-policy profiles that inherit the generated policy fields.")
    parser.add_argument("--profile-template", action="append", help="Optional PROFILE=TEMPLATE mapping where TEMPLATE is one of dev, staging, or prod. If omitted, matching profile names such as dev, staging, or prod use that preset automatically.")
    parser.add_argument("--profile-allow-inspection-warnings", action="append", help="Repeat PROFILE=true|false to override allow_inspection_warnings for a specific profile.")
    parser.add_argument("--profile-allow-source-not-ready", action="append", help="Repeat PROFILE=true|false to override allow_source_not_ready for a specific profile.")
    parser.add_argument("--profile-allow-active-lease", action="append", help="Repeat PROFILE=true|false to override allow_active_lease for a specific profile.")
    parser.add_argument("--profile-allow-expired-lease", action="append", help="Repeat PROFILE=true|false to override allow_expired_lease for a specific profile.")
    parser.add_argument("--profile-require-signature", action="append", help="Repeat PROFILE=true|false to override require_signature for a specific profile.")
    parser.add_argument("--profile-max-age-hours", action="append", help="Repeat PROFILE=<hours> to override max_age_hours for a specific profile.")
    parser.add_argument("--profile-allowed-updated-by", action="append", help="Repeat PROFILE=<actor> to append allowed Updated by values for a specific profile.")
    parser.add_argument("--profile-allowed-next-owner", action="append", help="Repeat PROFILE=<actor> to append allowed Next owner values for a specific profile.")
    parser.add_argument("--profile-allowed-signature-scheme", action="append", help="Repeat PROFILE=<scheme> to append allowed signature schemes for a specific profile.")
    parser.add_argument("--profile-allowed-signer", action="append", help="Repeat PROFILE=<actor> to append allowed signature signers for a specific profile.")
    parser.add_argument("--profile-allowed-key-id", action="append", help="Repeat PROFILE=<key-id> to append allowed key ids for a specific profile.")
    parser.add_argument("--profile-allowed-public-key-fingerprint", action="append", help="Repeat PROFILE=<SHA256:...> to append allowed SSH public key fingerprints for a specific profile.")
    parser.add_argument("--profile-revoked-signer", action="append", help="Repeat PROFILE=<actor> to append revoked signature signers for a specific profile.")
    parser.add_argument("--profile-revoked-key-id", action="append", help="Repeat PROFILE=<key-id> to append revoked key ids for a specific profile.")
    parser.add_argument("--profile-revoked-public-key-fingerprint", action="append", help="Repeat PROFILE=<SHA256:...> to append revoked SSH public key fingerprints for a specific profile.")
    parser.add_argument("--profile-signature-secret-env", action="append", help="Repeat PROFILE=<ENV_VAR> to override signature_secret_env for a specific profile.")
    parser.add_argument("--default-profile", help="Optional default trust-policy profile to apply automatically when the policy is loaded.")
    parser.add_argument("--signature-secret-env", default="HANDOFF_BUNDLE_SIGNING_SECRET", help="Environment variable used to look up the signature verification secret.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def materialize_policy(args: argparse.Namespace) -> dict[str, object]:
    policy = build_trust_policy(
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
        signature_secret_env=args.signature_secret_env,
    )
    materialized = {
        "allow_inspection_warnings": bool(policy["allow_inspection_warnings"]),
        "allow_source_not_ready": "not-ready" in policy["allowed_source_readiness"],
        "allow_active_lease": "active" in policy["allowed_lease_states"],
        "allow_expired_lease": "expired" in policy["allowed_lease_states"],
        "max_age_hours": policy["max_age_hours"],
        "allowed_updated_by": list(policy["allowed_updated_by"]),
        "allowed_next_owner": list(policy["allowed_next_owner"]),
        "require_signature": bool(policy["require_signature"]),
        "allowed_signature_schemes": list(policy["allowed_signature_schemes"]),
        "allowed_signers": list(policy["allowed_signers"]),
        "allowed_key_ids": list(policy["allowed_key_ids"]),
        "allowed_public_key_fingerprints": list(policy["allowed_public_key_fingerprints"]),
        "revoked_signers": list(policy["revoked_signers"]),
        "revoked_key_ids": list(policy["revoked_key_ids"]),
        "revoked_public_key_fingerprints": list(policy["revoked_public_key_fingerprints"]),
        "signature_secret_env": policy["signature_secret_env"],
    }
    if args.profile_name:
        declared_profiles = set(args.profile_name)
        if args.default_profile is not None and args.default_profile not in args.profile_name:
            raise ValueError(f"default_profile {args.default_profile!r} must also be declared via --profile-name.")
        template_map: dict[str, str] = {}
        for mapping in args.profile_template or []:
            if "=" not in mapping:
                raise ValueError(f"profile template mapping must look like PROFILE=TEMPLATE: {mapping!r}")
            profile_name, template_name = mapping.split("=", 1)
            profile_name = profile_name.strip()
            template_name = template_name.strip()
            if not profile_name:
                raise ValueError(f"profile template mapping must include a profile name: {mapping!r}")
            if profile_name not in declared_profiles:
                raise ValueError(f"profile template mapping references undeclared profile {profile_name!r}. Declare it via --profile-name first.")
            if template_name not in PROFILE_PRESETS:
                raise ValueError(f"Unknown profile template {template_name!r}. Expected one of: {', '.join(sorted(PROFILE_PRESETS))}.")
            template_map[profile_name] = template_name
        profile_bool_overrides = {
            "allow_inspection_warnings": parse_profile_bool_mappings(args.profile_allow_inspection_warnings, "--profile-allow-inspection-warnings", declared_profiles),
            "allow_source_not_ready": parse_profile_bool_mappings(args.profile_allow_source_not_ready, "--profile-allow-source-not-ready", declared_profiles),
            "allow_active_lease": parse_profile_bool_mappings(args.profile_allow_active_lease, "--profile-allow-active-lease", declared_profiles),
            "allow_expired_lease": parse_profile_bool_mappings(args.profile_allow_expired_lease, "--profile-allow-expired-lease", declared_profiles),
            "require_signature": parse_profile_bool_mappings(args.profile_require_signature, "--profile-require-signature", declared_profiles),
        }
        profile_int_overrides = {
            "max_age_hours": parse_profile_int_mappings(args.profile_max_age_hours, "--profile-max-age-hours", declared_profiles),
        }
        profile_list_overrides = {
            "allowed_updated_by": parse_profile_list_mappings(args.profile_allowed_updated_by, "--profile-allowed-updated-by", declared_profiles),
            "allowed_next_owner": parse_profile_list_mappings(args.profile_allowed_next_owner, "--profile-allowed-next-owner", declared_profiles),
            "allowed_signature_schemes": parse_profile_list_mappings(args.profile_allowed_signature_scheme, "--profile-allowed-signature-scheme", declared_profiles),
            "allowed_signers": parse_profile_list_mappings(args.profile_allowed_signer, "--profile-allowed-signer", declared_profiles),
            "allowed_key_ids": parse_profile_list_mappings(args.profile_allowed_key_id, "--profile-allowed-key-id", declared_profiles),
            "allowed_public_key_fingerprints": parse_profile_list_mappings(args.profile_allowed_public_key_fingerprint, "--profile-allowed-public-key-fingerprint", declared_profiles),
            "revoked_signers": parse_profile_list_mappings(args.profile_revoked_signer, "--profile-revoked-signer", declared_profiles),
            "revoked_key_ids": parse_profile_list_mappings(args.profile_revoked_key_id, "--profile-revoked-key-id", declared_profiles),
            "revoked_public_key_fingerprints": parse_profile_list_mappings(args.profile_revoked_public_key_fingerprint, "--profile-revoked-public-key-fingerprint", declared_profiles),
        }
        profile_string_overrides = {
            "signature_secret_env": parse_profile_string_mappings(args.profile_signature_secret_env, "--profile-signature-secret-env", declared_profiles),
        }
        materialized["default_profile"] = args.default_profile
        profiles: dict[str, dict[str, object]] = {}
        for profile_name in args.profile_name:
            profile_policy = {
                key: value for key, value in materialized.items() if key not in {"default_profile", "profiles"}
            }
            template_name = template_map.get(profile_name, infer_profile_template(profile_name))
            if template_name is not None:
                profile_policy.update(PROFILE_PRESETS[template_name])
            for field_name, override_map in profile_bool_overrides.items():
                if profile_name in override_map:
                    profile_policy[field_name] = override_map[profile_name]
            for field_name, override_map in profile_int_overrides.items():
                if profile_name in override_map:
                    profile_policy[field_name] = override_map[profile_name]
            for field_name, override_map in profile_list_overrides.items():
                if profile_name in override_map:
                    profile_policy[field_name] = override_map[profile_name]
            for field_name, override_map in profile_string_overrides.items():
                if profile_name in override_map:
                    profile_policy[field_name] = override_map[profile_name]
            profiles[profile_name] = profile_policy
        materialized["profiles"] = profiles
    elif args.default_profile is not None:
        raise ValueError("--default-profile requires at least one --profile-name.")
    elif args.profile_template:
        raise ValueError("--profile-template requires at least one --profile-name.")
    return materialized


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Policy: {payload['policy_path']}",
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


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    policy_path = Path(args.output).resolve() if args.output else (docs_root / DEFAULT_TRUST_POLICY_FILE_NAME).resolve()

    if policy_path.exists() and not args.force:
        return emit(
            {
                "result": "error",
                "policy_path": str(policy_path),
                "warnings": [],
                "errors": [f"Refusing to overwrite existing policy file: {policy_path}"],
            },
            args.format,
        )

    try:
        policy = materialize_policy(args)
    except ValueError as exc:
        return emit(
            {
                "result": "error",
                "policy_path": str(policy_path),
                "warnings": [],
                "errors": [str(exc)],
            },
            args.format,
        )
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    return emit(
        {
            "result": "generated",
            "policy_path": str(policy_path),
            "policy": policy,
            "warnings": [],
            "errors": [],
        },
        args.format,
    )


if __name__ == "__main__":
    raise SystemExit(main())
