#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from resolve_test_docs_root import resolve_docs_root  # type: ignore
from run_handoff_ci_checks import DEFAULT_CI_POLICY_FILE_NAME, load_ci_policy_file  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a handoff bundle CI policy JSON file."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--policy", help=f"Explicit CI policy path. Defaults to <docs-root>/{DEFAULT_CI_POLICY_FILE_NAME}.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Policy: {payload['policy_path']}",
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
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    policy_path = Path(args.policy).resolve() if args.policy else (docs_root / DEFAULT_CI_POLICY_FILE_NAME).resolve()

    try:
        policy = load_ci_policy_file(policy_path)
    except ValueError as exc:
        return emit(
            {
                "result": "error",
                "policy_path": str(policy_path),
                "errors": [str(exc)],
            },
            args.format,
        )

    return emit(
        {
            "result": "valid",
            "policy_path": str(policy_path),
            "policy": policy,
            "errors": [],
        },
        args.format,
    )


if __name__ == "__main__":
    raise SystemExit(main())
