#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_handoff_ci_checks import DEFAULT_CI_POLICY_FILE_NAME  # type: ignore
from resolve_test_docs_root import resolve_docs_root  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic handoff bundle CI policy JSON file."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--output", help=f"Explicit CI policy output path. Defaults to <docs-root>/{DEFAULT_CI_POLICY_FILE_NAME}.")
    parser.add_argument("--force", action="store_true", help="Overwrite the CI policy file if it already exists.")
    parser.add_argument("--require-portable-bundle-policies", action="store_true", help="Require the full checked-in portable bundle policy set, which implies both trust and redaction policies.")
    parser.add_argument("--require-trust-policy", action="store_true", help="Require the checked-in trust policy file in CI.")
    parser.add_argument("--require-redaction-policy", action="store_true", help="Require the checked-in redaction policy file in CI.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Policy: {payload['policy_path']}",
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
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    policy_path = Path(args.output).resolve() if args.output else (docs_root / DEFAULT_CI_POLICY_FILE_NAME).resolve()

    if policy_path.exists() and not args.force:
        return emit(
            {
                "result": "error",
                "policy_path": str(policy_path),
                "warnings": [],
                "errors": [f"Refusing to overwrite existing CI policy file: {policy_path}"],
            },
            args.format,
        )

    policy = {
        "require_trust_policy": args.require_trust_policy or args.require_portable_bundle_policies,
        "require_redaction_policy": args.require_redaction_policy or args.require_portable_bundle_policies,
        "require_portable_bundle_policies": args.require_portable_bundle_policies,
    }
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
