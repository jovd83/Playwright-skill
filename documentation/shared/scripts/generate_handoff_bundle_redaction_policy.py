#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from export_handoff_bundle import (  # type: ignore
    DEFAULT_REDACTION_POLICY_FILE_NAME,
    build_default_redaction_policy,
    merge_redaction_policy,
)
from resolve_test_docs_root import resolve_docs_root  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic handoff bundle redaction policy JSON file."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--output", help=f"Explicit policy output path. Defaults to <docs-root>/{DEFAULT_REDACTION_POLICY_FILE_NAME}.")
    parser.add_argument("--force", action="store_true", help="Overwrite the policy file if it already exists.")
    parser.add_argument("--allow-redaction-path", action="append", help="Repeat to exempt matching bundle paths from redaction.")
    parser.add_argument("--deny-redaction-path", action="append", help="Repeat to force-redact matching bundle paths.")
    parser.add_argument("--extra-sensitive-keyword", action="append", help="Repeat to treat more field-name keywords as sensitive.")
    parser.add_argument("--extra-redaction-regex", action="append", help="Repeat to add more regex patterns that should be redacted from string values.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def materialize_policy(args: argparse.Namespace) -> dict[str, object]:
    policy = merge_redaction_policy(
        build_default_redaction_policy(),
        allow_paths=args.allow_redaction_path,
        deny_paths=args.deny_redaction_path,
        extra_sensitive_keywords=args.extra_sensitive_keyword,
        extra_redaction_regexes=args.extra_redaction_regex,
    )
    return {
        "allow_paths": list(policy["allow_paths"]),
        "deny_paths": list(policy["deny_paths"]),
        "extra_sensitive_keywords": list(policy["extra_sensitive_keywords"]),
        "extra_redaction_regexes": list(policy["extra_redaction_regexes"]),
    }


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
    policy_path = Path(args.output).resolve() if args.output else (docs_root / DEFAULT_REDACTION_POLICY_FILE_NAME).resolve()

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

    policy = materialize_policy(args)
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
