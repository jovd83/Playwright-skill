#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from export_handoff_bundle import DEFAULT_REDACTION_POLICY_FILE_NAME  # type: ignore
from handoff_bundle_trust import DEFAULT_TRUST_POLICY_FILE_NAME  # type: ignore
from resolve_test_docs_root import resolve_docs_root  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"
DEFAULT_CI_POLICY_FILE_NAME = "handoff-bundle-ci-policy.json"

PY_COMPILE_TARGETS = (
    SHARED_SCRIPTS / "handoff_bundle_trust.py",
    SHARED_SCRIPTS / "check_handoff_bundle_trust.py",
    SHARED_SCRIPTS / "generate_handoff_bundle_trust_policy.py",
    SHARED_SCRIPTS / "validate_handoff_bundle_trust_policy.py",
    SHARED_SCRIPTS / "generate_handoff_bundle_ci_policy.py",
    SHARED_SCRIPTS / "validate_handoff_bundle_ci_policy.py",
    SHARED_SCRIPTS / "generate_handoff_bundle_redaction_policy.py",
    SHARED_SCRIPTS / "validate_handoff_bundle_redaction_policy.py",
    SHARED_SCRIPTS / "export_handoff_bundle.py",
    SHARED_SCRIPTS / "inspect_handoff_bundle.py",
    SHARED_SCRIPTS / "import_handoff_bundle.py",
    SHARED_SCRIPTS / "smoke_test_handoff_workflow.py",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the deterministic handoff/session-state CI checks."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root and docs-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery for trust policy validation.")
    parser.add_argument("--ci-policy-file", help=f"Explicit CI policy path. Defaults to <docs-root>/{DEFAULT_CI_POLICY_FILE_NAME} when present.")
    parser.add_argument("--no-ci-policy-file", action="store_true", help="Ignore default CI policy discovery and rely only on CLI enforcement flags.")
    parser.add_argument("--require-ci-policy", action="store_true", help="Fail if the checked-in CI policy file is missing.")
    parser.add_argument("--require-trust-policy", action="store_true", help="Fail if the checked-in trust policy file is missing.")
    parser.add_argument("--require-redaction-policy", action="store_true", help="Fail if the checked-in redaction policy file is missing.")
    parser.add_argument("--skip-policy", action="store_true", help="Skip validation of the checked-in trust policy file.")
    parser.add_argument("--skip-redaction-policy", action="store_true", help="Skip validation of the checked-in redaction policy file.")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip the shared smoke test.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def run_command(command: list[str], cwd: Path) -> tuple[int, str, str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Docs root: {payload['docs_root']}",
        "Checks:",
    ]
    for check in payload["checks"]:
        lines.append(f"- {check['name']}: {check['result']}")
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


def resolve_ci_policy_path(docs_root: Path, explicit_policy_path: str | None, use_default_policy_file: bool) -> Path | None:
    if explicit_policy_path:
        return Path(explicit_policy_path).resolve()
    if not use_default_policy_file:
        return None
    candidate = (docs_root / DEFAULT_CI_POLICY_FILE_NAME).resolve()
    if candidate.exists():
        return candidate
    return None


def load_ci_policy_file(policy_path: Path) -> dict[str, bool]:
    try:
        raw = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"CI policy file does not exist: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"CI policy file is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("CI policy root must be a JSON object.")
    allowed_keys = {"require_trust_policy", "require_redaction_policy", "require_portable_bundle_policies"}
    unknown_keys = sorted(key for key in raw if key not in allowed_keys)
    if unknown_keys:
        raise ValueError(f"CI policy file contains unknown keys: {', '.join(unknown_keys)}")
    policy: dict[str, bool] = {"require_trust_policy": False, "require_redaction_policy": False, "require_portable_bundle_policies": False}
    for key in policy:
        value = raw.get(key, False)
        if not isinstance(value, bool):
            raise ValueError(f"{key} must be true or false.")
        policy[key] = value
    if policy["require_portable_bundle_policies"]:
        policy["require_trust_policy"] = True
        policy["require_redaction_policy"] = True
    return policy


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    try:
        ci_policy_path = resolve_ci_policy_path(docs_root, args.ci_policy_file, not args.no_ci_policy_file)
        ci_policy = load_ci_policy_file(ci_policy_path) if ci_policy_path else {"require_trust_policy": False, "require_redaction_policy": False, "require_portable_bundle_policies": False}
    except ValueError as exc:
        payload = {
            "result": "error",
            "docs_root": str(docs_root),
            "ci_policy_path": str(ci_policy_path) if 'ci_policy_path' in locals() and ci_policy_path else "None",
            "checks": [],
            "errors": [str(exc)],
        }
        return emit(payload, args.format)

    checks: list[dict[str, object]] = []
    errors: list[str] = []

    py_compile_command = [sys.executable, "-m", "py_compile", *(str(path) for path in PY_COMPILE_TARGETS)]
    rc, stdout, stderr = run_command(py_compile_command, REPO_ROOT)
    checks.append({"name": "py_compile", "result": "passed" if rc == 0 else "failed"})
    if rc != 0:
        errors.append(f"py_compile failed: {(stderr or stdout).strip()}")

    policy_path = docs_root / DEFAULT_TRUST_POLICY_FILE_NAME
    if args.skip_policy:
        checks.append({"name": "trust_policy", "result": "skipped"})
    elif policy_path.exists():
        rc, stdout, stderr = run_command(
            [sys.executable, str(SHARED_SCRIPTS / "validate_handoff_bundle_trust_policy.py"), "--root", str(docs_root), "--format", "json"],
            REPO_ROOT,
        )
        checks.append({"name": "trust_policy", "result": "passed" if rc == 0 else "failed"})
        if rc != 0:
            errors.append(f"trust_policy failed: {(stderr or stdout).strip()}")
    else:
        checks.append({"name": "trust_policy", "result": "not-present"})
        if ci_policy["require_trust_policy"] or args.require_trust_policy:
            errors.append(f"trust_policy failed: required policy file is missing: {policy_path}")

    if ci_policy_path is None:
        checks.append({"name": "ci_policy", "result": "not-present"})
        if args.require_ci_policy:
            errors.append(f"ci_policy failed: required policy file is missing: {docs_root / DEFAULT_CI_POLICY_FILE_NAME}")
    else:
        checks.append({"name": "ci_policy", "result": "passed"})

    redaction_policy_path = docs_root / DEFAULT_REDACTION_POLICY_FILE_NAME
    if args.skip_redaction_policy:
        checks.append({"name": "redaction_policy", "result": "skipped"})
    elif redaction_policy_path.exists():
        rc, stdout, stderr = run_command(
            [sys.executable, str(SHARED_SCRIPTS / "validate_handoff_bundle_redaction_policy.py"), "--root", str(docs_root), "--format", "json"],
            REPO_ROOT,
        )
        checks.append({"name": "redaction_policy", "result": "passed" if rc == 0 else "failed"})
        if rc != 0:
            errors.append(f"redaction_policy failed: {(stderr or stdout).strip()}")
    else:
        checks.append({"name": "redaction_policy", "result": "not-present"})
        if ci_policy["require_redaction_policy"] or args.require_redaction_policy:
            errors.append(f"redaction_policy failed: required policy file is missing: {redaction_policy_path}")

    if args.skip_smoke:
        checks.append({"name": "smoke", "result": "skipped"})
    else:
        rc, stdout, stderr = run_command(
            [sys.executable, str(SHARED_SCRIPTS / "smoke_test_handoff_workflow.py")],
            REPO_ROOT,
        )
        checks.append({"name": "smoke", "result": "passed" if rc == 0 else "failed"})
        if rc != 0:
            errors.append(f"smoke failed: {(stderr or stdout).strip()}")

    payload = {
        "result": "ok" if not errors else "error",
        "docs_root": str(docs_root),
        "ci_policy_path": str(ci_policy_path) if ci_policy_path else "None",
        "checks": checks,
        "errors": errors,
    }
    return emit(payload, args.format)


if __name__ == "__main__":
    raise SystemExit(main())
