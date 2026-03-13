#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import fnmatch
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"

if str(SHARED_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SHARED_SCRIPTS))

from check_handoff_readiness import build_readiness_payload  # type: ignore  # noqa: E402
from handoff_bundle import BUNDLE_VERSION, attach_bundle_integrity  # type: ignore  # noqa: E402
from handoff_lease import (  # type: ignore  # noqa: E402
    inspect_lease,
    lease_path_for_docs_root,
    load_lease_file,
    resolve_live_pair,
)
from report_handoff_workspace import build_workspace_report  # type: ignore  # noqa: E402
from resolve_test_docs_root import find_project_root  # type: ignore  # noqa: E402


SENSITIVE_KEYWORDS = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_key",
    "client_secret",
    "authorization",
)
DEFAULT_REDACTION_POLICY_FILE_NAME = "handoff-bundle-redaction-policy.json"
ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b([A-Z0-9._-]*(?:password|passwd|secret|token|api[_-]?key|access[_-]?key|client[_-]?secret|authorization)[A-Z0-9._-]*)(\s*[:=]\s*)([^\s,;]+)"
)
BEARER_PATTERN = re.compile(r"(?i)(bearer\s+)([A-Za-z0-9._~+/\-=]+)")
BASIC_PATTERN = re.compile(r"(?i)(basic\s+)([A-Za-z0-9+/=]+)")
JWT_PATTERN = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+\b")
GITHUB_TOKEN_PATTERN = re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")
GITHUB_FINE_GRAINED_TOKEN_PATTERN = re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")
AWS_ACCESS_KEY_PATTERN = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
SLACK_TOKEN_PATTERN = re.compile(r"\bxox(?:a|b|p|o|r|s)-[A-Za-z0-9-]{10,}\b")
SLACK_WEBHOOK_PATTERN = re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/_-]+")
NPM_TOKEN_PATTERN = re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")
GITLAB_TOKEN_PATTERN = re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")
OPENAI_KEY_PATTERN = re.compile(r"\bsk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{20,}\b")
ANTHROPIC_KEY_PATTERN = re.compile(r"\bsk-ant-(?:api\d{2}-)?[A-Za-z0-9_-]{20,}\b")
GOOGLE_API_KEY_PATTERN = re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")
HUGGINGFACE_TOKEN_PATTERN = re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")
DISCORD_WEBHOOK_PATTERN = re.compile(r"https://discord(?:app)?\.com/api/webhooks/[0-9]{16,}/[A-Za-z0-9._-]+")
MAILCHIMP_API_KEY_PATTERN = re.compile(r"\b[a-f0-9]{32}-us\d{1,2}\b", re.IGNORECASE)
SENDGRID_API_KEY_PATTERN = re.compile(r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\b")
SHOPIFY_ADMIN_TOKEN_PATTERN = re.compile(r"\bshpat_[A-Fa-f0-9]{32}\b")
TWILIO_API_KEY_PATTERN = re.compile(r"\bSK[0-9A-Fa-f]{32}\b")
POSTMAN_API_KEY_PATTERN = re.compile(r"\bPMAK-[0-9A-Fa-f-]{20,}\b")
STRIPE_SECRET_PATTERN = re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b")
PRIVATE_KEY_BLOCK_PATTERN = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----", re.DOTALL)
DEFAULT_REDACTION_REGEX_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key-block", PRIVATE_KEY_BLOCK_PATTERN),
    ("github-token", GITHUB_TOKEN_PATTERN),
    ("github-fine-grained-token", GITHUB_FINE_GRAINED_TOKEN_PATTERN),
    ("aws-access-key", AWS_ACCESS_KEY_PATTERN),
    ("slack-token", SLACK_TOKEN_PATTERN),
    ("slack-webhook", SLACK_WEBHOOK_PATTERN),
    ("npm-token", NPM_TOKEN_PATTERN),
    ("gitlab-token", GITLAB_TOKEN_PATTERN),
    ("openai-key", OPENAI_KEY_PATTERN),
    ("anthropic-key", ANTHROPIC_KEY_PATTERN),
    ("google-api-key", GOOGLE_API_KEY_PATTERN),
    ("huggingface-token", HUGGINGFACE_TOKEN_PATTERN),
    ("discord-webhook", DISCORD_WEBHOOK_PATTERN),
    ("mailchimp-api-key", MAILCHIMP_API_KEY_PATTERN),
    ("sendgrid-api-key", SENDGRID_API_KEY_PATTERN),
    ("shopify-admin-token", SHOPIFY_ADMIN_TOKEN_PATTERN),
    ("twilio-api-key", TWILIO_API_KEY_PATTERN),
    ("postman-api-key", POSTMAN_API_KEY_PATTERN),
    ("stripe-secret", STRIPE_SECRET_PATTERN),
    ("jwt", JWT_PATTERN),
)


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def default_bundle_name() -> str:
    return f"{datetime.now().strftime('%Y%m%d_%H%M')}_handoff-bundle.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export the current linked handoff pair, lease context, and workspace snapshot into a portable JSON bundle."
    )
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument("--output", help="Optional explicit output path for the JSON bundle.")
    parser.add_argument("--redaction-policy-file", help=f"Optional JSON file with allow/deny redaction rules. Defaults to <docs-root>/{DEFAULT_REDACTION_POLICY_FILE_NAME} when present.")
    parser.add_argument("--no-redaction-policy-file", action="store_true", help="Ignore the default checked-in redaction policy discovery and use only built-in defaults plus CLI overrides.")
    parser.add_argument("--allow-redaction-path", action="append", help="Repeat to exempt matching bundle paths from redaction, for example bundle.git.commit_sha.")
    parser.add_argument("--deny-redaction-path", action="append", help="Repeat to force-redact matching bundle paths, for example bundle.documents.handover_markdown.")
    parser.add_argument("--extra-sensitive-keyword", action="append", help="Repeat to treat more field-name keywords as sensitive.")
    parser.add_argument("--extra-redaction-regex", action="append", help="Repeat to add more regex patterns that should be redacted from string values.")
    parser.add_argument("--no-redact-secrets", action="store_true", help="Disable best-effort redaction of obvious secret material from the exported bundle.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output bundle if it already exists.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args()


def load_raw_lease_payload(lease_path: Path) -> tuple[dict[str, object] | None, list[str]]:
    if not lease_path.exists():
        return None, []
    try:
        payload = load_lease_file(lease_path)
    except json.JSONDecodeError as exc:
        return None, [f"Lease payload could not be copied into the bundle because the lease file is not valid JSON: {exc}"]
    if payload is None:
        return None, []
    return payload, []


def keyword_is_sensitive(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(keyword in normalized for keyword in SENSITIVE_KEYWORDS)


def build_default_redaction_policy() -> dict[str, object]:
    return {
        "allow_paths": [],
        "deny_paths": [],
        "extra_sensitive_keywords": [],
        "extra_redaction_regexes": [],
    }


def load_redaction_policy_file(policy_path: Path) -> dict[str, object]:
    try:
        raw = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Redaction policy file does not exist: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Redaction policy file is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("Redaction policy root must be a JSON object.")
    allowed_keys = {"allow_paths", "deny_paths", "extra_sensitive_keywords", "extra_redaction_regexes"}
    unknown_keys = sorted(key for key in raw if key not in allowed_keys)
    if unknown_keys:
        raise ValueError(f"Redaction policy file contains unknown keys: {', '.join(unknown_keys)}")
    policy = build_default_redaction_policy()
    for key in ("allow_paths", "deny_paths", "extra_sensitive_keywords", "extra_redaction_regexes"):
        value = raw.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            raise ValueError(f"Redaction policy field {key} must be a JSON array of non-empty strings.")
        policy[key] = [item.strip() for item in value]
    return policy


def resolve_redaction_policy_path(
    docs_root: Path,
    *,
    explicit_policy_path: str | None = None,
    use_default_policy_file: bool = True,
) -> Path | None:
    if explicit_policy_path:
        return Path(explicit_policy_path).resolve()
    if not use_default_policy_file:
        return None
    candidate = (docs_root / DEFAULT_REDACTION_POLICY_FILE_NAME).resolve()
    if candidate.exists():
        return candidate
    return None


def merge_redaction_policy(
    base_policy: dict[str, object],
    *,
    allow_paths: list[str] | None = None,
    deny_paths: list[str] | None = None,
    extra_sensitive_keywords: list[str] | None = None,
    extra_redaction_regexes: list[str] | None = None,
) -> dict[str, object]:
    policy = {
        "allow_paths": list(base_policy.get("allow_paths", [])),
        "deny_paths": list(base_policy.get("deny_paths", [])),
        "extra_sensitive_keywords": list(base_policy.get("extra_sensitive_keywords", [])),
        "extra_redaction_regexes": list(base_policy.get("extra_redaction_regexes", [])),
    }
    if allow_paths is not None:
        policy["allow_paths"] = allow_paths
    if deny_paths is not None:
        policy["deny_paths"] = deny_paths
    if extra_sensitive_keywords is not None:
        policy["extra_sensitive_keywords"] = extra_sensitive_keywords
    if extra_redaction_regexes is not None:
        policy["extra_redaction_regexes"] = extra_redaction_regexes
    return policy


def path_matches(patterns: list[str], path_label: str) -> bool:
    return any(fnmatch.fnmatchcase(path_label, pattern) for pattern in patterns)


def keyword_is_sensitive(key: str, extra_sensitive_keywords: list[str]) -> bool:
    normalized = key.lower().replace("-", "_")
    keywords = [*SENSITIVE_KEYWORDS, *(keyword.lower().replace("-", "_") for keyword in extra_sensitive_keywords)]
    return any(keyword in normalized for keyword in keywords)


def compile_extra_regexes(patterns: list[str]) -> list[tuple[str, re.Pattern[str]]]:
    compiled: list[tuple[str, re.Pattern[str]]] = []
    for index, pattern in enumerate(patterns, start=1):
        try:
            compiled.append((f"extra-regex-{index}", re.compile(pattern)))
        except re.error as exc:
            raise ValueError(f"Invalid extra redaction regex {pattern!r}: {exc}") from exc
    return compiled


def redact_string(
    value: str,
    path_label: str,
    *,
    regex_rules: list[tuple[str, re.Pattern[str]]],
) -> tuple[str, list[dict[str, str]]]:
    hits: list[dict[str, str]] = []

    def assignment_replacer(match: re.Match[str]) -> str:
        hits.append({"path": path_label, "rule": "assignment"})
        return f"{match.group(1)}{match.group(2)}[REDACTED]"

    def bearer_replacer(match: re.Match[str]) -> str:
        hits.append({"path": path_label, "rule": "bearer"})
        return f"{match.group(1)}[REDACTED]"

    def basic_replacer(match: re.Match[str]) -> str:
        hits.append({"path": path_label, "rule": "basic-auth"})
        return f"{match.group(1)}[REDACTED]"

    redacted = BEARER_PATTERN.sub(bearer_replacer, value)
    redacted = BASIC_PATTERN.sub(basic_replacer, redacted)
    redacted = ASSIGNMENT_PATTERN.sub(assignment_replacer, redacted)
    for rule_name, pattern in regex_rules:
        def generic_replacer(match: re.Match[str], *, _rule_name: str = rule_name) -> str:
            hits.append({"path": path_label, "rule": _rule_name})
            return "[REDACTED]"
        redacted = pattern.sub(generic_replacer, redacted)
    return redacted, hits


def redact_bundle_value(
    value: Any,
    *,
    path_parts: list[str],
    policy: dict[str, object],
    regex_rules: list[tuple[str, re.Pattern[str]]],
) -> tuple[Any, list[dict[str, str]]]:
    path_label = ".".join(path_parts)
    allow_paths = list(policy.get("allow_paths", []))
    deny_paths = list(policy.get("deny_paths", []))
    if path_matches(allow_paths, path_label):
        return value, []
    if path_matches(deny_paths, path_label):
        return "[REDACTED]", [{"path": path_label, "rule": "deny-path"}]
    if isinstance(value, dict):
        redacted_dict: dict[str, Any] = {}
        hits: list[dict[str, str]] = []
        for key, item in value.items():
            child_parts = [*path_parts, str(key)]
            child_label = ".".join(child_parts)
            if path_matches(allow_paths, child_label):
                redacted_dict[key] = item
                continue
            if path_matches(deny_paths, child_label):
                redacted_dict[key] = "[REDACTED]"
                hits.append({"path": child_label, "rule": "deny-path"})
                continue
            if keyword_is_sensitive(str(key), list(policy.get("extra_sensitive_keywords", []))):
                redacted_dict[key] = "[REDACTED]"
                hits.append({"path": ".".join(child_parts), "rule": "sensitive-key"})
                continue
            redacted_item, child_hits = redact_bundle_value(
                item,
                path_parts=child_parts,
                policy=policy,
                regex_rules=regex_rules,
            )
            redacted_dict[key] = redacted_item
            hits.extend(child_hits)
        return redacted_dict, hits
    if isinstance(value, list):
        redacted_items: list[Any] = []
        hits: list[dict[str, str]] = []
        for index, item in enumerate(value):
            redacted_item, child_hits = redact_bundle_value(
                item,
                path_parts=[*path_parts, str(index)],
                policy=policy,
                regex_rules=regex_rules,
            )
            redacted_items.append(redacted_item)
            hits.extend(child_hits)
        return redacted_items, hits
    if isinstance(value, str):
        return redact_string(value, path_label, regex_rules=regex_rules)
    return value, []


def summarize_redactions(enabled: bool, hits: list[dict[str, str]], policy: dict[str, object], policy_source: str) -> dict[str, object]:
    redacted_paths: list[str] = []
    rules_triggered: list[str] = []
    for hit in hits:
        path = hit["path"]
        rule = hit["rule"]
        if path not in redacted_paths:
            redacted_paths.append(path)
        if rule not in rules_triggered:
            rules_triggered.append(rule)
    return {
        "enabled": enabled,
        "policy_source": policy_source,
        "redaction_count": len(hits),
        "redacted_paths": redacted_paths[:50],
        "rules_triggered": rules_triggered,
        "allow_paths": list(policy.get("allow_paths", [])),
        "deny_paths": list(policy.get("deny_paths", [])),
        "extra_sensitive_keywords": list(policy.get("extra_sensitive_keywords", [])),
        "extra_redaction_regex_count": len(list(policy.get("extra_redaction_regexes", []))),
    }


def run_git(project_root: Path, args: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), *args],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return False, str(exc)
    if result.returncode != 0:
        return False, result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed"
    return True, result.stdout.strip()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def capture_git_context(docs_root: Path) -> dict[str, object]:
    project_root = find_project_root(docs_root)
    git_dir = project_root / ".git"
    if not git_dir.exists():
        return {
            "available": False,
            "project_root": str(project_root),
            "branch": "None",
            "commit_sha": "None",
            "is_dirty": False,
            "dirty_paths": [],
            "dirty_fingerprint": "None",
            "status_fingerprint": "None",
            "error": "No .git directory was found while walking up from the documentation root.",
        }

    branch_ok, branch_output = run_git(project_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    commit_ok, commit_output = run_git(project_root, ["rev-parse", "HEAD"])
    status_ok, status_output = run_git(project_root, ["status", "--short"])
    diff_ok, diff_output = run_git(project_root, ["diff", "--no-ext-diff", "--no-color", "HEAD", "--"])
    numstat_ok, numstat_output = run_git(project_root, ["diff", "--numstat", "--no-ext-diff", "--no-color", "HEAD", "--"])
    if not branch_ok or not commit_ok or not status_ok or not diff_ok or not numstat_ok:
        errors = [output for ok, output in ((branch_ok, branch_output), (commit_ok, commit_output), (status_ok, status_output)) if not ok]
        if not diff_ok:
            errors.append(diff_output)
        if not numstat_ok:
            errors.append(numstat_output)
        return {
            "available": False,
            "project_root": str(project_root),
            "branch": "None",
            "commit_sha": "None",
            "is_dirty": False,
            "dirty_paths": [],
            "dirty_fingerprint": "None",
            "status_fingerprint": "None",
            "patch_summary_fingerprint": "None",
            "changed_file_count": 0,
            "added_line_count": 0,
            "deleted_line_count": 0,
            "patch_summary": [],
            "error": "; ".join(errors),
        }

    dirty_lines = [line for line in status_output.splitlines() if line.strip()]
    dirty_paths = [line[3:].strip() if len(line) > 3 else line.strip() for line in dirty_lines]
    status_fingerprint = text_sha256(status_output) if status_output else "clean"
    dirty_fingerprint = text_sha256(f"STATUS\n{status_output}\nDIFF\n{diff_output}") if dirty_lines else "clean"
    patch_summary: list[dict[str, object]] = []
    added_line_count = 0
    deleted_line_count = 0
    if numstat_ok and numstat_output.strip():
        for raw_line in numstat_output.splitlines():
            parts = raw_line.split("\t")
            if len(parts) != 3:
                continue
            added_raw, deleted_raw, path = parts
            added = int(added_raw) if added_raw.isdigit() else 0
            deleted = int(deleted_raw) if deleted_raw.isdigit() else 0
            added_line_count += added
            deleted_line_count += deleted
            patch_summary.append({"path": path, "added": added, "deleted": deleted})
    patch_summary_fingerprint = text_sha256(numstat_output) if numstat_output.strip() else "clean"
    return {
        "available": True,
        "project_root": str(project_root),
        "branch": branch_output or "HEAD",
        "commit_sha": commit_output,
        "is_dirty": bool(dirty_lines),
        "dirty_paths": dirty_paths[:100],
        "dirty_fingerprint": dirty_fingerprint,
        "status_fingerprint": status_fingerprint,
        "patch_summary_fingerprint": patch_summary_fingerprint,
        "changed_file_count": len(patch_summary),
        "added_line_count": added_line_count,
        "deleted_line_count": deleted_line_count,
        "patch_summary": patch_summary[:50],
        "error": "None",
    }


def build_export_payload(
    docs_root: Path,
    handover_path: Path,
    session_path: Path,
    source: str,
    output_path: Path,
    redact_secrets: bool,
    redaction_policy: dict[str, object],
    redaction_policy_source: str,
) -> tuple[dict[str, object], dict[str, object]]:
    report = build_workspace_report(start_dir=docs_root, explicit_root=str(docs_root), history_limit=3)
    readiness = build_readiness_payload(report)
    lease_inspection = inspect_lease(start_dir=docs_root, explicit_root=str(docs_root))
    raw_lease_payload, lease_copy_warnings = load_raw_lease_payload(lease_path_for_docs_root(docs_root))
    git_context = capture_git_context(docs_root)

    bundle_without_integrity = {
        "bundle_version": BUNDLE_VERSION,
        "exported_at": current_timestamp(),
        "source": {
            "resolution": source,
            "docs_root": str(docs_root),
            "handover": str(handover_path),
            "session_state": str(session_path),
            "handover_name": handover_path.name,
            "session_state_name": session_path.name,
        },
        "documents": {
            "handover_markdown": handover_path.read_text(encoding="utf-8"),
            "session_state_markdown": session_path.read_text(encoding="utf-8"),
        },
        "lease": {
            "payload": raw_lease_payload,
            "inspection": lease_inspection,
        },
        "report": report,
        "readiness": readiness,
        "git": git_context,
    }
    redaction_hits: list[dict[str, str]] = []
    if redact_secrets:
        regex_rules = [*DEFAULT_REDACTION_REGEX_RULES, *compile_extra_regexes(list(redaction_policy.get("extra_redaction_regexes", [])))]
        bundle_without_integrity, redaction_hits = redact_bundle_value(
            bundle_without_integrity,
            path_parts=["bundle"],
            policy=redaction_policy,
            regex_rules=regex_rules,
        )
    bundle_without_integrity["redaction"] = summarize_redactions(redact_secrets, redaction_hits, redaction_policy, redaction_policy_source)
    bundle = attach_bundle_integrity(bundle_without_integrity)

    warnings = [*lease_copy_warnings]
    warnings.extend(f"WORKSPACE: {warning}" for warning in report["warnings"])
    warnings.extend(f"WORKSPACE: {error}" for error in report["errors"])
    if redact_secrets and redaction_hits:
        warnings.append(f"REDACTION: Redacted {len(redaction_hits)} secret-like values from the exported bundle.")
    result = "exported-with-warnings" if warnings else "exported"
    payload = {
        "result": result,
        "bundle_path": str(output_path),
        "docs_root": str(docs_root),
        "source": source,
        "handover": str(handover_path),
        "session_state": str(session_path),
        "lease_state": lease_inspection["state"],
        "readiness_verdict": readiness["verdict"],
        "git_available": git_context["available"],
        "git_dirty": git_context["is_dirty"],
        "redaction_count": len(redaction_hits),
        "warnings": warnings,
        "errors": [],
    }
    return bundle, payload


def format_text(payload: dict[str, object]) -> str:
    lines = [
        f"Result: {payload['result']}",
        f"Bundle: {payload['bundle_path']}",
        f"Docs root: {payload['docs_root']}",
        f"Source: {payload['source']}",
        f"Handover: {payload['handover']}",
        f"Session-state: {payload['session_state']}",
        f"Lease state: {payload['lease_state']}",
        f"Readiness verdict: {payload['readiness_verdict']}",
        f"Git available: {payload['git_available']}",
        f"Git dirty: {payload['git_dirty']}",
        f"Redaction count: {payload['redaction_count']}",
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

    try:
        docs_root, handover_path, session_path, source = resolve_live_pair(start_dir=start_dir, explicit_root=args.root)
    except ValueError as exc:
        payload = {
            "result": "error",
            "bundle_path": "None",
            "docs_root": "None",
            "source": "None",
            "handover": "None",
            "session_state": "None",
            "lease_state": "none",
            "readiness_verdict": "unknown",
            "git_available": False,
            "git_dirty": False,
            "redaction_count": 0,
            "warnings": [],
            "errors": [str(exc)],
        }
        return emit(payload, args.format)

    output_path = Path(args.output).resolve() if args.output else (docs_root / "handoff-bundles" / default_bundle_name()).resolve()
    if output_path.exists() and not args.force:
        payload = {
            "result": "error",
            "bundle_path": str(output_path),
            "docs_root": str(docs_root),
            "source": source,
            "handover": str(handover_path),
            "session_state": str(session_path),
            "lease_state": "unknown",
            "readiness_verdict": "unknown",
            "git_available": False,
            "git_dirty": False,
            "redaction_count": 0,
            "warnings": [],
            "errors": [f"Refusing to overwrite existing bundle: {output_path}"],
        }
        return emit(payload, args.format)

    try:
        redaction_policy_path = resolve_redaction_policy_path(
            docs_root,
            explicit_policy_path=args.redaction_policy_file,
            use_default_policy_file=not args.no_redaction_policy_file,
        )
        base_redaction_policy = load_redaction_policy_file(redaction_policy_path) if redaction_policy_path else build_default_redaction_policy()
        redaction_policy = merge_redaction_policy(
            base_redaction_policy,
            allow_paths=args.allow_redaction_path,
            deny_paths=args.deny_redaction_path,
            extra_sensitive_keywords=args.extra_sensitive_keyword,
            extra_redaction_regexes=args.extra_redaction_regex,
        )
        bundle, payload = build_export_payload(
            docs_root=docs_root,
            handover_path=handover_path,
            session_path=session_path,
            source=source,
            output_path=output_path,
            redact_secrets=not args.no_redact_secrets,
            redaction_policy=redaction_policy,
            redaction_policy_source=str(redaction_policy_path) if redaction_policy_path else "default",
        )
    except ValueError as exc:
        payload = {
            "result": "error",
            "bundle_path": str(output_path),
            "docs_root": str(docs_root),
            "source": source,
            "handover": str(handover_path),
            "session_state": str(session_path),
            "lease_state": "unknown",
            "readiness_verdict": "unknown",
            "git_available": False,
            "git_dirty": False,
            "redaction_count": 0,
            "warnings": [],
            "errors": [str(exc)],
        }
        return emit(payload, args.format)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return emit(payload, args.format)


if __name__ == "__main__":
    raise SystemExit(main())
