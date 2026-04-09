#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
RESOLVER = REPO_ROOT / "documentation" / "shared" / "scripts" / "resolve_test_docs_root.py"
PAIR_RESOLVER = REPO_ROOT / "documentation" / "shared" / "scripts" / "resolve_latest_handoff_pair.py"
PAIR_GENERATOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "generate_handoff_pair.py"
PAIR_ARCHIVER = REPO_ROOT / "documentation" / "shared" / "scripts" / "archive_handoff_pair.py"
PAIR_HISTORY = REPO_ROOT / "documentation" / "shared" / "scripts" / "list_handoff_history.py"
PAIR_RESTORER = REPO_ROOT / "documentation" / "shared" / "scripts" / "restore_handoff_pair.py"
RECONCILER = REPO_ROOT / "documentation" / "shared" / "scripts" / "reconcile_handoff_pair.py"
WORKSPACE_AUDITOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "audit_handoff_workspace.py"
WORKSPACE_REPAIRER = REPO_ROOT / "documentation" / "shared" / "scripts" / "repair_handoff_workspace.py"
LEASE_MANAGER = REPO_ROOT / "documentation" / "shared" / "scripts" / "manage_handoff_lease.py"
WORKSPACE_REPORTER = REPO_ROOT / "documentation" / "shared" / "scripts" / "report_handoff_workspace.py"
READINESS_CHECKER = REPO_ROOT / "documentation" / "shared" / "scripts" / "check_handoff_readiness.py"
SESSION_BEGINNER = REPO_ROOT / "documentation" / "shared" / "scripts" / "begin_handoff_session.py"
SESSION_ENDER = REPO_ROOT / "documentation" / "shared" / "scripts" / "end_handoff_session.py"
BUNDLE_EXPORTER = REPO_ROOT / "documentation" / "shared" / "scripts" / "export_handoff_bundle.py"
BUNDLE_INSPECTOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "inspect_handoff_bundle.py"
BUNDLE_SIGNER = REPO_ROOT / "documentation" / "shared" / "scripts" / "sign_handoff_bundle.py"
BUNDLE_SIGNATURE_VERIFIER = REPO_ROOT / "documentation" / "shared" / "scripts" / "verify_handoff_bundle_signature.py"
BUNDLE_TRUST_CHECKER = REPO_ROOT / "documentation" / "shared" / "scripts" / "check_handoff_bundle_trust.py"
BUNDLE_TRUST_POLICY_GENERATOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "generate_handoff_bundle_trust_policy.py"
BUNDLE_TRUST_POLICY_VALIDATOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "validate_handoff_bundle_trust_policy.py"
BUNDLE_CI_POLICY_GENERATOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "generate_handoff_bundle_ci_policy.py"
BUNDLE_CI_POLICY_VALIDATOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "validate_handoff_bundle_ci_policy.py"
BUNDLE_REDACTION_POLICY_GENERATOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "generate_handoff_bundle_redaction_policy.py"
BUNDLE_REDACTION_POLICY_VALIDATOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "validate_handoff_bundle_redaction_policy.py"
BUNDLE_IMPORTER = REPO_ROOT / "documentation" / "shared" / "scripts" / "import_handoff_bundle.py"
CI_CHECK_RUNNER = REPO_ROOT / "documentation" / "shared" / "scripts" / "run_handoff_ci_checks.py"
PAIR_VALIDATOR = REPO_ROOT / "documentation" / "shared" / "scripts" / "validate_handoff_pair.py"
PAIR_SUMMARIZER = REPO_ROOT / "documentation" / "shared" / "scripts" / "summarize_handoff_pair.py"
PAIR_UPDATER = REPO_ROOT / "documentation" / "shared" / "scripts" / "update_handoff_pair.py"
HANDOVER_GENERATOR = REPO_ROOT / "documentation" / "handover" / "scripts" / "generate_handover.py"
HANDOVER_VALIDATOR = REPO_ROOT / "documentation" / "handover" / "scripts" / "validate_handover.py"
HANDOVER_AGENT_METADATA = REPO_ROOT / "documentation" / "handover" / "agents" / "openai.yaml"
SESSION_GENERATOR = REPO_ROOT / "documentation" / "session-state" / "scripts" / "generate_session_state.py"
SESSION_VALIDATOR = REPO_ROOT / "documentation" / "session-state" / "scripts" / "validate_session_state.py"
SESSION_AGENT_METADATA = REPO_ROOT / "documentation" / "session-state" / "agents" / "openai.yaml"

# Fake tokens constructed at runtime via concatenation to avoid triggering
# GitHub secret-scanning push protection.  The assembled values still match
# the redaction regexes in export_handoff_bundle.py.
_FAKE_SLACK_TOKEN = "xoxb-" + "1234567890-abcdefghijklmnop"
_FAKE_OPENAI_KEY = "sk-" + "test_1234567890abcdefghijklmnop"
_FAKE_GITLAB_TOKEN = "glpat-" + "abcdefghijklmnopqrstuvwxyz123456"
_FAKE_GOOGLE_KEY = "AIza" + "SyA123456789012345678901234567890123"
_FAKE_HF_TOKEN = "hf_" + "abcdefghijklmnopqrstuvwxyz123456"
_FAKE_DISCORD_WEBHOOK = (
    "https://discord.com/api/webhooks/"
    + "123456789012345678/abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)
_FAKE_MAILCHIMP_KEY = "0123456789abcdef0123456789abcdef" + "-us19"
_FAKE_SENDGRID_KEY = "SG." + "abcdefghijklmnopQRSTUVWX.abcdefghijklmnopqrstuvwxyz123456"
_FAKE_SHOPIFY_TOKEN = "shpat_" + "0123456789abcdef0123456789abcdef"
_FAKE_TWILIO_KEY = "SK" + "0123456789abcdef0123456789abcdef"
_FAKE_POSTMAN_KEY = "PMAK-" + "01234567-89ab-cdef-0123-456789abcdef"
_ALL_FAKE_TOKENS_COMMAND = (
    f"API_TOKEN=super-secret-token {_FAKE_SLACK_TOKEN} {_FAKE_OPENAI_KEY}"
    f" {_FAKE_GITLAB_TOKEN} {_FAKE_GOOGLE_KEY} {_FAKE_HF_TOKEN}"
    f" {_FAKE_DISCORD_WEBHOOK} {_FAKE_MAILCHIMP_KEY} {_FAKE_SENDGRID_KEY}"
    f" {_FAKE_SHOPIFY_TOKEN} {_FAKE_TWILIO_KEY} {_FAKE_POSTMAN_KEY}"
    f" python documentation/shared/scripts/import_handoff_bundle.py"
    f" --bundle portable-handoff.json --format json"
)


class SmokeTestError(RuntimeError):
    pass


def run_python(script: Path, args: list[str], cwd: Path, expected_returncode: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.returncode != expected_returncode:
        raise SmokeTestError(
            f"Command failed: {script.name} {' '.join(args)}\n"
            f"cwd={cwd}\n"
            f"expected={expected_returncode}, actual={result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def assert_equal(actual: object, expected: object, message: str) -> None:
    if actual != expected:
        raise SmokeTestError(f"{message}\nexpected={expected!r}\nactual={actual!r}")


def assert_contains(text: str, fragment: str, message: str) -> None:
    if fragment not in text:
        raise SmokeTestError(f"{message}\nmissing fragment={fragment!r}\ntext:\n{text}")


def run_command(command: list[str], cwd: Path, expected_returncode: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode != expected_returncode:
        raise SmokeTestError(
            f"Command failed: {' '.join(command)}\n"
            f"cwd={cwd}\n"
            f"expected={expected_returncode}, actual={result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def generate_ssh_keypair(private_key_path: Path, comment: str) -> tuple[Path, str]:
    run_command(
        [
            "ssh-keygen",
            "-t",
            "ed25519",
            "-N",
            "",
            "-C",
            comment,
            "-f",
            str(private_key_path),
        ],
        cwd=private_key_path.parent,
    )
    public_key_path = private_key_path.with_suffix(".pub")
    fingerprint_output = run_command(["ssh-keygen", "-l", "-f", str(public_key_path)], cwd=private_key_path.parent).stdout.strip()
    fingerprint = fingerprint_output.split()[1]
    return public_key_path, fingerprint


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SmokeTestError(f"Could not find text to replace in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_section_value(path: Path, section_heading: str, new_value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() == section_heading:
            if index + 1 >= len(lines):
                raise SmokeTestError(f"Section {section_heading!r} has no value line in {path}")
            lines[index + 1] = new_value
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise SmokeTestError(f"Could not find section {section_heading!r} in {path}")


def replace_section_body(path: Path, section_heading: str, new_body: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    end = len(lines)
    for index, line in enumerate(lines):
        if line.strip() == section_heading:
            start = index
            continue
        if start is not None and line.startswith("## "):
            end = index
            break
    if start is None:
        raise SmokeTestError(f"Could not find section {section_heading!r} in {path}")

    replacement = [lines[start], *new_body.splitlines()]
    updated = [*lines[:start], *replacement, *lines[end:]]
    path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")


def test_default_root_and_link_validation(tmp_root: Path) -> None:
    project_root = tmp_root / "fallback-project"
    (project_root / ".git").mkdir(parents=True)
    shared_timestamp = "2026-03-12T09:01:15+01:00"

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "both"], cwd=REPO_ROOT)
    docs_root = Path(result.stdout.strip())
    expected_root = project_root / "docs" / "tests"
    assert_equal(docs_root.resolve(), expected_root.resolve(), "Resolver did not fall back to docs/tests.")
    assert (docs_root / "handovers").exists()
    assert (docs_root / "session-state").exists()

    result = run_python(
        SESSION_GENERATOR,
        [
            "--task",
            "Smoke test root resolution",
            "--status",
            "in-progress",
            "--last-updated",
            shared_timestamp,
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--last-completed-step",
            "Initialized temp project",
            "--current-step",
            "Generating handover",
            "--remaining-step",
            "Run validators",
            "--file-touched",
            "docs/tests/session-state/CURRENT.md",
            "--command-to-resume",
            f"python {HANDOVER_VALIDATOR} docs/tests/handovers/sample_handover.md",
        ],
        cwd=project_root,
    )
    session_path = Path(result.stdout.strip())
    assert_equal(session_path.resolve(), (docs_root / "session-state" / "CURRENT.md").resolve(), "Session-state generator used the wrong root.")

    handover_path = docs_root / "handovers" / "sample_handover.md"
    result = run_python(
        HANDOVER_GENERATOR,
        [
            "--output",
            str(handover_path),
            "--task-summary",
            "Smoke test root resolution",
            "--status",
            "in-progress",
            "--last-updated",
            shared_timestamp,
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--what-was-done",
            "Initialized temp project",
            "--last-completed-step",
            "Initialized temp project",
            "--current-step",
            "Generating handover",
            "--remaining-work",
            "Run validators",
            "--first-file",
            "docs/tests/session-state/CURRENT.md",
            "--next-command",
            f"python {HANDOVER_VALIDATOR} docs/tests/handovers/sample_handover.md",
        ],
        cwd=project_root,
    )
    assert_equal(Path(result.stdout.strip()).resolve(), handover_path.resolve(), "Handover generator wrote to the wrong path.")

    run_python(
        SESSION_GENERATOR,
        [
            "--task",
            "Smoke test root resolution",
            "--status",
            "in-progress",
            "--last-updated",
            shared_timestamp,
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--last-completed-step",
            "Initialized temp project",
            "--current-step",
            "Generating handover",
            "--remaining-step",
            "Run validators",
            "--file-touched",
            "docs/tests/session-state/CURRENT.md",
            "--command-to-resume",
            f"python {HANDOVER_VALIDATOR} docs/tests/handovers/sample_handover.md",
            "--handover-pointer",
            "../handovers/sample_handover.md",
            "--force",
        ],
        cwd=project_root,
    )

    result = run_python(HANDOVER_VALIDATOR, ["docs/tests/handovers/sample_handover.md"], cwd=project_root)
    assert_contains(result.stdout, "Valid handover", "Expected the handover validator to pass.")

    result = run_python(SESSION_VALIDATOR, ["docs/tests/session-state/CURRENT.md"], cwd=project_root)
    assert_contains(result.stdout, "Valid session-state file", "Expected the session-state validator to pass.")

    result = run_python(PAIR_VALIDATOR, ["--session-state", str(session_path)], cwd=project_root)
    assert_contains(result.stdout, "Valid handoff pair", "Expected the pair validator to pass using pointer discovery.")

    result = run_python(PAIR_SUMMARIZER, ["--session-state", str(session_path), "--format", "json"], cwd=project_root)
    summary = json.loads(result.stdout)
    assert_equal(summary["status"], "in-progress", "Expected summary status to match the linked pair.")
    assert_equal(summary["next_owner"], "qa-reviewer", "Expected summary next owner to match the linked pair.")
    assert_equal(summary["resume"]["first_file"], "docs/tests/session-state/CURRENT.md", "Expected summary to expose the first file to open.")
    assert_equal(summary["warnings"], [], "Expected no warnings for the valid linked pair.")

    invalid_handover = docs_root / "handovers" / "invalid_no_timezone.md"
    shutil.copy2(handover_path, invalid_handover)
    replace_section_value(invalid_handover, "## Last updated", "2026-03-12T22:10:00")
    result = run_python(HANDOVER_VALIDATOR, [str(invalid_handover)], cwd=project_root, expected_returncode=1)
    assert_contains(result.stderr, "timezone offset", "Expected timezone validation to fail.")

    invalid_handover_pointer = docs_root / "handovers" / "invalid_pointer_separators.md"
    shutil.copy2(handover_path, invalid_handover_pointer)
    replace_section_value(invalid_handover_pointer, "## Session-state pointer", "..\\session-state\\CURRENT.md")
    result = run_python(HANDOVER_VALIDATOR, [str(invalid_handover_pointer)], cwd=project_root, expected_returncode=1)
    assert_contains(result.stderr, "forward slashes", "Expected the handover validator to reject backslash separators.")

    invalid_session = docs_root / "session-state" / "invalid_placeholder.md"
    shutil.copy2(session_path, invalid_session)
    replace_once(invalid_session, "codex", "<human-or-agent-id>")
    result = run_python(SESSION_VALIDATOR, [str(invalid_session)], cwd=project_root, expected_returncode=1)
    assert_contains(result.stderr, "unresolved placeholder", "Expected placeholder validation to fail.")

    invalid_session_pointer = docs_root / "session-state" / "invalid_pointer_separators.md"
    shutil.copy2(session_path, invalid_session_pointer)
    replace_section_value(invalid_session_pointer, "## Handover pointer", "..\\handovers\\sample_handover.md")
    result = run_python(SESSION_VALIDATOR, [str(invalid_session_pointer)], cwd=project_root, expected_returncode=1)
    assert_contains(result.stderr, "forward slashes", "Expected the session-state validator to reject backslash separators.")

    replace_section_value(handover_path, "## Status", "ready-for-review")
    replace_section_value(session_path, "## Status", "blocked")
    replace_section_value(session_path, "## Next owner", "infra-team")
    replace_section_value(session_path, "## Current step", "Waiting for staging secret")
    replace_section_body(session_path, "## Blockers", "- Missing staging API token\n- Needed to unblock: Provision the secret")

    result = run_python(
        PAIR_VALIDATOR,
        [
            "--handover",
            str(handover_path),
            "--session-state",
            str(session_path),
        ],
        cwd=project_root,
        expected_returncode=1,
    )
    assert_contains(result.stderr, "Status mismatch", "Expected the pair validator to detect mismatched statuses.")

    result = run_python(PAIR_SUMMARIZER, ["--handover", str(handover_path), "--format", "json"], cwd=project_root)
    summary = json.loads(result.stdout)
    assert_contains(summary["warnings"][0], "Status mismatch", "Expected the summary to surface pair warnings.")

    result = run_python(
        RECONCILER,
        [
            "--handover",
            str(handover_path),
            "--session-state",
            str(session_path),
            "--updated-by",
            "codex",
        ],
        cwd=project_root,
    )
    assert_contains(result.stdout, "status=blocked", "Expected the reconciler to keep the pair blocked.")
    assert_contains(result.stdout, "next_owner=infra-team", "Expected the reconciler to keep the session-state next owner.")

    result = run_python(HANDOVER_VALIDATOR, [str(handover_path)], cwd=project_root)
    assert_contains(result.stdout, "Valid handover", "Expected reconciled handover to validate.")

    result = run_python(SESSION_VALIDATOR, [str(session_path)], cwd=project_root)
    assert_contains(result.stdout, "Valid session-state file", "Expected reconciled session-state to validate.")

    result = run_python(PAIR_VALIDATOR, ["--handover", str(handover_path)], cwd=project_root)
    assert_contains(result.stdout, "Valid handoff pair", "Expected the reconciled pair to validate together.")

    result = run_python(PAIR_SUMMARIZER, ["--handover", str(handover_path), "--strict"], cwd=project_root)
    assert_contains(result.stdout, "Warnings:\n- None", "Expected strict summary to succeed with no warnings after reconciliation.")

    handover_text = handover_path.read_text(encoding="utf-8")
    session_text = session_path.read_text(encoding="utf-8")
    assert_contains(handover_text, "## Status\nblocked", "Expected the reconciled handover status to be blocked.")
    assert_contains(session_text, "## Status\nblocked", "Expected the reconciled session-state status to be blocked.")
    assert_contains(handover_text, "## Next owner\ninfra-team", "Expected the reconciled handover next owner to match the session-state file.")
    assert_contains(session_text, "## Handover pointer\n../handovers/sample_handover.md", "Expected reconciled handover pointer to remain relative.")


def test_existing_root_preferred(tmp_root: Path) -> None:
    project_root = tmp_root / "preferred-root-project"
    (project_root / ".git").mkdir(parents=True)
    preferred_root = project_root / "test-docs"
    preferred_root.mkdir(parents=True)

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "session-state"], cwd=REPO_ROOT)
    resolved_root = Path(result.stdout.strip())
    assert_equal(resolved_root.resolve(), preferred_root.resolve(), "Resolver did not prefer the existing test-docs directory.")
    assert (preferred_root / "session-state").exists()

    result = run_python(
        SESSION_GENERATOR,
        [
            "--task",
            "Smoke test preferred root",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
        ],
        cwd=project_root,
    )
    generated_path = Path(result.stdout.strip())
    assert_equal(
        generated_path.resolve(),
        (preferred_root / "session-state" / "CURRENT.md").resolve(),
        "Session-state generator did not prefer the existing root.",
    )


def test_done_session_preserves_explicit_handover_pointer(tmp_root: Path) -> None:
    project_root = tmp_root / "done-session-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "both"], cwd=REPO_ROOT)
    docs_root = Path(result.stdout.strip())
    snapshot_path = docs_root / "session-state" / "done_snapshot.md"

    result = run_python(
        SESSION_GENERATOR,
        [
            "--task",
            "Smoke test done snapshot",
            "--status",
            "done",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--handover-pointer",
            "../handovers/final_handover.md",
            "--output",
            str(snapshot_path),
        ],
        cwd=project_root,
    )
    assert_equal(Path(result.stdout.strip()).resolve(), snapshot_path.resolve(), "Done snapshot wrote to the wrong path.")

    snapshot_text = snapshot_path.read_text(encoding="utf-8")
    assert_contains(snapshot_text, "## Next owner\nNone", "Expected done snapshots to normalize Next owner to None.")
    assert_contains(
        snapshot_text,
        "## Handover pointer\n../handovers/final_handover.md",
        "Expected explicit handover pointers to survive done-state generation.",
    )


def test_pair_generator_creates_consistent_pair(tmp_root: Path) -> None:
    project_root = tmp_root / "pair-generator-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "both"], cwd=REPO_ROOT)
    docs_root = Path(result.stdout.strip())
    handover_path = docs_root / "handovers" / "pair_generator_handover.md"
    session_path = docs_root / "session-state" / "CURRENT.md"
    shared_timestamp = "2026-03-12T10:15:00+01:00"

    result = run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Smoke test pair generator",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--last-updated",
            shared_timestamp,
            "--what-was-done",
            "Created a synchronized handoff pair",
            "--last-completed-step",
            "Created a synchronized handoff pair",
            "--current-step",
            "Waiting for review",
            "--remaining-step",
            "Run final pair validation",
            "--file-touched",
            "docs/tests/session-state/CURRENT.md",
            "--command-to-resume",
            f"python {PAIR_VALIDATOR} --session-state docs/tests/session-state/CURRENT.md",
            "--handover-output",
            str(handover_path),
            "--session-output",
            str(session_path),
        ],
        cwd=project_root,
    )
    assert_contains(result.stdout, "Generated handoff pair", "Expected the pair generator to report success.")

    result = run_python(PAIR_VALIDATOR, ["--handover", str(handover_path)], cwd=project_root)
    assert_contains(result.stdout, "Valid handoff pair", "Expected the generated pair to validate.")

    handover_text = handover_path.read_text(encoding="utf-8")
    session_text = session_path.read_text(encoding="utf-8")
    assert_contains(handover_text, f"## Last updated\n{shared_timestamp}", "Expected shared handover timestamp.")
    assert_contains(session_text, f"## Last updated\n{shared_timestamp}", "Expected shared session-state timestamp.")
    assert_contains(handover_text, "## Session-state pointer\n../session-state/CURRENT.md", "Expected linked session-state pointer.")
    assert_contains(session_text, "## Handover pointer\n../handovers/pair_generator_handover.md", "Expected linked handover pointer.")

    result = run_python(PAIR_SUMMARIZER, ["--handover", str(handover_path)], cwd=project_root)
    assert_contains(result.stdout, "Task: Smoke test pair generator", "Expected text summary to show the task.")
    assert_contains(result.stdout, "Warnings:\n- None", "Expected text summary to show a clean pair.")


def test_pair_updater_preserves_and_syncs_pair(tmp_root: Path) -> None:
    project_root = tmp_root / "pair-updater-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "both"], cwd=REPO_ROOT)
    docs_root = Path(result.stdout.strip())
    handover_path = docs_root / "handovers" / "pair_updater_handover.md"
    session_path = docs_root / "session-state" / "CURRENT.md"

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Smoke test pair updater",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--what-was-done",
            "Created the initial linked pair",
            "--last-completed-step",
            "Created the initial linked pair",
            "--current-step",
            "Waiting for the next milestone",
            "--remaining-step",
            "Run the updater",
            "--file-touched",
            "docs/tests/session-state/CURRENT.md",
            "--command-to-resume",
            f"python {PAIR_UPDATER} --session-state docs/tests/session-state/CURRENT.md --updated-by codex",
            "--handover-output",
            str(handover_path),
            "--session-output",
            str(session_path),
        ],
        cwd=project_root,
    )

    result = run_python(
        PAIR_UPDATER,
        [
            "--session-state",
            str(session_path),
            "--updated-by",
            "codex",
            "--status",
            "blocked",
            "--next-owner",
            "infra-team",
            "--current-step",
            "Waiting for the staging secret",
            "--remaining-step",
            "Provision the staging secret",
            "--what-was-done",
            "Created the initial linked pair",
            "--what-was-done",
            "Attempted the environment handoff",
            "--blocker",
            "Missing staging API token",
            "--command-to-resume",
            "python documentation/shared/scripts/validate_handoff_pair.py --session-state docs/tests/session-state/CURRENT.md",
        ],
        cwd=project_root,
    )
    assert_contains(result.stdout, "Updated handoff pair: status=blocked, next_owner=infra-team", "Expected the updater to report the synchronized state.")

    result = run_python(PAIR_VALIDATOR, ["--handover", str(handover_path)], cwd=project_root)
    assert_contains(result.stdout, "Valid handoff pair", "Expected the updated pair to validate.")

    result = run_python(PAIR_SUMMARIZER, ["--handover", str(handover_path), "--format", "json"], cwd=project_root)
    summary = json.loads(result.stdout)
    assert_equal(summary["status"], "blocked", "Expected the updater to synchronize the status.")
    assert_equal(summary["next_owner"], "infra-team", "Expected the updater to synchronize the next owner.")
    assert_contains(summary["what_was_done"][1], "Attempted the environment handoff", "Expected appended work to be present after replacement.")
    assert_equal(summary["remaining_steps"], ["Provision the staging secret"], "Expected the updater to replace remaining steps.")
    assert_equal(summary["blockers"], ["Missing staging API token"], "Expected the updater to replace blockers.")


def test_latest_pair_resolver_and_zero_arg_tools(tmp_root: Path) -> None:
    project_root = tmp_root / "latest-pair-current-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "both"], cwd=REPO_ROOT)
    docs_root = Path(result.stdout.strip())
    handover_path = docs_root / "handovers" / "20260312_1115_handover.md"

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Smoke test latest pair with CURRENT",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--what-was-done",
            "Created the current linked pair",
            "--last-completed-step",
            "Created the current linked pair",
            "--current-step",
            "Waiting for the next operator",
            "--remaining-step",
            "Run zero-arg tools",
            "--command-to-resume",
            "python documentation/shared/scripts/validate_handoff_pair.py",
            "--handover-output",
            str(handover_path),
        ],
        cwd=project_root,
    )

    result = run_python(PAIR_RESOLVER, ["--format", "json"], cwd=project_root)
    resolution = json.loads(result.stdout)
    assert_equal(Path(resolution["handover"]).resolve(), handover_path.resolve(), "Expected resolver to use the CURRENT.md pointer handover.")
    assert_equal(resolution["source"], "current-pointer", "Expected resolver to prefer CURRENT.md when it is linked.")

    result = run_python(PAIR_VALIDATOR, [], cwd=project_root)
    assert_contains(result.stdout, "Valid handoff pair", "Expected zero-arg pair validation to resolve the current pair.")

    result = run_python(PAIR_SUMMARIZER, ["--format", "json"], cwd=project_root)
    summary = json.loads(result.stdout)
    assert_equal(summary["task"], "Smoke test latest pair with CURRENT", "Expected zero-arg summary to resolve the current pair.")

    result = run_python(
        PAIR_UPDATER,
        [
            "--updated-by",
            "codex",
            "--status",
            "ready-for-review",
            "--current-step",
            "Ready for review",
            "--remaining-step",
            "Collect reviewer feedback",
        ],
        cwd=project_root,
    )
    assert_contains(result.stdout, "Updated handoff pair: status=ready-for-review", "Expected zero-arg updater to resolve the current pair.")

    result = run_python(RECONCILER, ["--updated-by", "codex"], cwd=project_root)
    assert_contains(result.stdout, "Reconciled pair", "Expected zero-arg reconciler to resolve the current pair.")


def test_latest_pair_resolver_without_current(tmp_root: Path) -> None:
    project_root = tmp_root / "latest-pair-snapshot-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "both"], cwd=REPO_ROOT)
    docs_root = Path(result.stdout.strip())
    older_handover = docs_root / "handovers" / "20260312_0900_handover.md"
    older_session = docs_root / "session-state" / "20260312_0900_session-state.md"
    latest_handover = docs_root / "handovers" / "20260312_1130_handover.md"
    latest_session = docs_root / "session-state" / "20260312_1130_session-state.md"

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Older snapshot pair",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--handover-output",
            str(older_handover),
            "--session-output",
            str(older_session),
        ],
        cwd=project_root,
    )

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Latest snapshot pair",
            "--status",
            "blocked",
            "--updated-by",
            "codex",
            "--next-owner",
            "infra-team",
            "--blocker",
            "Waiting for staging credentials",
            "--handover-output",
            str(latest_handover),
            "--session-output",
            str(latest_session),
        ],
        cwd=project_root,
    )

    result = run_python(PAIR_RESOLVER, ["--format", "json"], cwd=project_root)
    resolution = json.loads(result.stdout)
    assert_equal(Path(resolution["handover"]).resolve(), latest_handover.resolve(), "Expected resolver to choose the latest snapshot handover.")
    assert_equal(Path(resolution["session_state"]).resolve(), latest_session.resolve(), "Expected resolver to choose the linked latest snapshot session-state.")
    assert_equal(resolution["source"], "latest-handover-pointer", "Expected resolver to prefer the latest handover pointer when CURRENT.md is absent.")

    result = run_python(PAIR_SUMMARIZER, ["--format", "json"], cwd=project_root)
    summary = json.loads(result.stdout)
    assert_equal(summary["task"], "Latest snapshot pair", "Expected zero-arg summary to resolve the latest snapshot pair.")
    assert_equal(summary["status"], "blocked", "Expected zero-arg summary to preserve the latest snapshot status.")


def test_pair_archiver_creates_snapshot_pair(tmp_root: Path) -> None:
    project_root = tmp_root / "pair-archiver-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "both"], cwd=REPO_ROOT)
    docs_root = Path(result.stdout.strip())
    live_handover = docs_root / "handovers" / "20260312_1200_handover.md"

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Live pair for archiving",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--what-was-done",
            "Created the live pair",
            "--last-completed-step",
            "Created the live pair",
            "--current-step",
            "Waiting for archive",
            "--remaining-step",
            "Archive the current pair",
            "--handover-output",
            str(live_handover),
        ],
        cwd=project_root,
    )

    result = run_python(PAIR_ARCHIVER, ["--timestamp", "20260312_1215"], cwd=project_root)
    assert_contains(result.stdout, "Archived handoff pair: timestamp=20260312_1215", "Expected the archiver to report the snapshot timestamp.")

    archived_handover = docs_root / "handovers" / "20260312_1215_handover.md"
    archived_session = docs_root / "session-state" / "20260312_1215_session-state.md"
    result = run_python(PAIR_VALIDATOR, ["--handover", str(archived_handover)], cwd=project_root)
    assert_contains(result.stdout, "Valid handoff pair", "Expected the archived pair to validate.")

    archived_handover_text = archived_handover.read_text(encoding="utf-8")
    archived_session_text = archived_session.read_text(encoding="utf-8")
    live_session_text = (docs_root / "session-state" / "CURRENT.md").read_text(encoding="utf-8")
    assert_contains(archived_handover_text, "## Session-state pointer\n../session-state/20260312_1215_session-state.md", "Expected the archived handover to point to the archived session snapshot.")
    assert_contains(archived_session_text, "## Handover pointer\n../handovers/20260312_1215_handover.md", "Expected the archived session snapshot to point to the archived handover.")
    assert_contains(live_session_text, "## Handover pointer\n../handovers/20260312_1200_handover.md", "Expected archiving to leave the live CURRENT.md pair untouched.")

    result = run_python(PAIR_HISTORY, ["--format", "json"], cwd=project_root)
    history = json.loads(result.stdout)
    assert_equal(history["active"]["task"], "Live pair for archiving", "Expected history to expose the live active pair.")
    assert_equal(history["active"]["kind"], "live", "Expected active history entry to remain live.")
    assert_equal(history["history"][0]["stamp"], "20260312_1215", "Expected archived milestone to appear in history.")


def test_pair_history_without_current(tmp_root: Path) -> None:
    project_root = tmp_root / "pair-history-snapshot-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "both"], cwd=REPO_ROOT)
    docs_root = Path(result.stdout.strip())
    older_handover = docs_root / "handovers" / "20260312_0800_handover.md"
    older_session = docs_root / "session-state" / "20260312_0800_session-state.md"
    latest_handover = docs_root / "handovers" / "20260312_1230_handover.md"
    latest_session = docs_root / "session-state" / "20260312_1230_session-state.md"

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Older history snapshot",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--handover-output",
            str(older_handover),
            "--session-output",
            str(older_session),
        ],
        cwd=project_root,
    )

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Latest history snapshot",
            "--status",
            "done",
            "--updated-by",
            "codex",
            "--next-owner",
            "None",
            "--handover-output",
            str(latest_handover),
            "--session-output",
            str(latest_session),
        ],
        cwd=project_root,
    )

    result = run_python(PAIR_HISTORY, ["--format", "json"], cwd=project_root)
    history = json.loads(result.stdout)
    assert_equal(history["active"]["task"], "Latest history snapshot", "Expected history to resolve the latest snapshot as active when CURRENT.md is absent.")
    assert_equal(history["active"]["kind"], "snapshot", "Expected snapshot mode when CURRENT.md is absent.")
    assert_equal(history["history"][0]["task"], "Latest history snapshot", "Expected latest snapshot first in history.")
    assert_equal(history["history"][1]["task"], "Older history snapshot", "Expected older snapshot second in history.")


def test_pair_restorer_reactivates_archived_snapshot(tmp_root: Path) -> None:
    project_root = tmp_root / "pair-restorer-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(RESOLVER, ["--start-dir", str(project_root), "--ensure", "both"], cwd=REPO_ROOT)
    docs_root = Path(result.stdout.strip())
    live_handover = docs_root / "handovers" / "20260312_1300_handover.md"

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Archived pair to restore",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--last-completed-step",
            "Created the live pair",
            "--current-step",
            "Waiting for archive",
            "--remaining-step",
            "Restore this archived state later",
            "--handover-output",
            str(live_handover),
        ],
        cwd=project_root,
    )

    run_python(PAIR_ARCHIVER, ["--timestamp", "20260312_1315"], cwd=project_root)

    run_python(
        PAIR_UPDATER,
        [
            "--updated-by",
            "codex",
            "--status",
            "blocked",
            "--next-owner",
            "infra-team",
            "--current-step",
            "Diverged from the archived snapshot",
            "--remaining-step",
            "Do not keep this state",
        ],
        cwd=project_root,
    )

    result = run_python(
        PAIR_RESTORER,
        [
            "--timestamp",
            "20260312_1315",
            "--updated-by",
            "codex",
            "--last-updated",
            "2026-03-12T13:30:00+01:00",
            "--restore-timestamp",
            "20260312_1330",
            "--force",
        ],
        cwd=project_root,
    )
    assert_contains(result.stdout, "Restored handoff pair: status=in-progress, next_owner=qa-reviewer", "Expected the restorer to reactivate the archived pair state.")

    restored_handover = docs_root / "handovers" / "20260312_1330_handover.md"
    result = run_python(PAIR_VALIDATOR, [], cwd=project_root)
    assert_contains(result.stdout, "Valid handoff pair", "Expected the restored live pair to validate.")

    result = run_python(PAIR_SUMMARIZER, ["--format", "json"], cwd=project_root)
    summary = json.loads(result.stdout)
    assert_equal(summary["task"], "Archived pair to restore", "Expected the restored live pair to keep the archived task.")
    assert_equal(summary["status"], "in-progress", "Expected the restored live pair to recover the archived status.")
    assert_equal(summary["next_owner"], "qa-reviewer", "Expected the restored live pair to recover the archived next owner.")
    assert_equal(summary["current_step"], "Waiting for archive", "Expected the restored live pair to recover the archived current step.")

    restored_session_text = (docs_root / "session-state" / "CURRENT.md").read_text(encoding="utf-8")
    archived_session_text = (docs_root / "session-state" / "20260312_1315_session-state.md").read_text(encoding="utf-8")
    assert_contains(restored_session_text, "## Handover pointer\n../handovers/20260312_1330_handover.md", "Expected CURRENT.md to point to the restored live handover.")
    assert_contains(archived_session_text, "## Handover pointer\n../handovers/20260312_1315_handover.md", "Expected the archived snapshot to remain untouched.")
    assert_contains(restored_handover.read_text(encoding="utf-8"), "## Last updated\n2026-03-12T13:30:00+01:00", "Expected the restored live handover timestamp to be refreshed.")


def test_workspace_auditor_reports_clean_warnings_and_errors(tmp_root: Path) -> None:
    project_root = tmp_root / "workspace-auditor-project"
    (project_root / ".git").mkdir(parents=True)

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Audit the full handoff workspace",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--what-was-done",
            "Created the active linked pair",
            "--last-completed-step",
            "Created the active linked pair",
            "--current-step",
            "Preparing archive coverage",
            "--remaining-step",
            "Run workspace audit",
            "--handover-output",
            "docs/tests/handovers/active_handover.md",
        ],
        cwd=project_root,
    )
    docs_root = project_root / "docs" / "tests"

    run_python(PAIR_ARCHIVER, ["--timestamp", "20260312_1415"], cwd=project_root)

    result = run_python(WORKSPACE_AUDITOR, ["--format", "json"], cwd=project_root)
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "clean", "Expected the workspace audit to pass for a clean active plus archived pair.")
    assert_equal(payload["totals"]["snapshot_pairs"], 1, "Expected the workspace audit to count the archived snapshot pair.")
    assert_equal(payload["warnings"], [], "Expected no warnings for the clean workspace audit.")
    assert_equal(payload["errors"], [], "Expected no errors for the clean workspace audit.")

    orphan_session = docs_root / "session-state" / "20260312_1420_session-state.md"
    shutil.copy2(docs_root / "session-state" / "CURRENT.md", orphan_session)
    replace_section_value(orphan_session, "## Status", "done")
    replace_section_value(orphan_session, "## Last updated", "2026-03-12T14:20:00+01:00")
    replace_section_value(orphan_session, "## Next owner", "None")
    replace_section_value(orphan_session, "## Handover pointer", "None")

    result = run_python(WORKSPACE_AUDITOR, ["--format", "json"], cwd=project_root)
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "warning", "Expected the workspace audit to downgrade to warning for partial history.")
    assert_contains(
        "\n".join(payload["warnings"]),
        "Snapshot session-state has no timestamp-matched handover snapshot: 20260312_1420_session-state.md",
        "Expected the workspace audit to warn about orphan session snapshots.",
    )
    assert_equal(payload["errors"], [], "Expected no hard errors for an otherwise valid orphan snapshot.")

    archived_session = docs_root / "session-state" / "20260312_1415_session-state.md"
    replace_section_value(archived_session, "## Handover pointer", "../handovers/missing_handover.md")

    result = run_python(WORKSPACE_AUDITOR, ["--format", "json"], cwd=project_root, expected_returncode=1)
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "error", "Expected the workspace audit to fail for a broken archived pair.")
    assert_contains(
        "\n".join(payload["errors"]),
        "20260312_1415_session-state.md: Handover pointer does not exist: ../handovers/missing_handover.md",
        "Expected the workspace audit to surface the broken archived pointer.",
    )


def test_workspace_repairer_fixes_live_and_snapshot_drift(tmp_root: Path) -> None:
    project_root = tmp_root / "workspace-repairer-project"
    (project_root / ".git").mkdir(parents=True)

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Repair the handoff workspace",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--what-was-done",
            "Created the live pair",
            "--last-completed-step",
            "Created the live pair",
            "--current-step",
            "Preparing repairs",
            "--remaining-step",
            "Run workspace repair",
            "--handover-output",
            "docs/tests/handovers/active_handover.md",
        ],
        cwd=project_root,
    )
    docs_root = project_root / "docs" / "tests"
    active_handover = docs_root / "handovers" / "active_handover.md"
    current_session = docs_root / "session-state" / "CURRENT.md"

    run_python(PAIR_ARCHIVER, ["--timestamp", "20260312_1515"], cwd=project_root)
    archived_handover = docs_root / "handovers" / "20260312_1515_handover.md"
    archived_session = docs_root / "session-state" / "20260312_1515_session-state.md"

    replace_section_value(active_handover, "## Status", "ready-for-review")
    replace_section_value(active_handover, "## Session-state pointer", "..\\session-state\\CURRENT.md")
    replace_section_value(current_session, "## Status", "blocked")
    replace_section_value(current_session, "## Next owner", "infra-team")
    replace_section_value(current_session, "## Current step", "Waiting for staging approval")
    replace_section_value(current_session, "## Handover pointer", "../handovers/active_handover.md")
    replace_section_body(current_session, "## Blockers", "- Missing staging approval\n- Needed to unblock: Approve the deployment window")

    replace_section_value(archived_handover, "## Session-state pointer", "..\\session-state\\broken.md")
    replace_section_value(archived_session, "## Handover pointer", "../handovers/missing_archive.md")

    result = run_python(WORKSPACE_AUDITOR, ["--format", "json"], cwd=project_root, expected_returncode=1)
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "error", "Expected the workspace audit to fail before repair.")

    result = run_python(WORKSPACE_REPAIRER, ["--updated-by", "codex", "--format", "json"], cwd=project_root)
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "clean", "Expected the workspace repairer to restore a clean workspace.")
    assert_equal(payload["active_pair"]["status"], "blocked", "Expected the live pair repair to preserve the blocked state.")
    assert_equal(payload["active_pair"]["next_owner"], "infra-team", "Expected the live pair repair to preserve the next owner.")
    assert_equal(payload["active_pair"]["changed"], True, "Expected the live pair repair to change the active pair.")
    assert_equal(payload["repairs"]["snapshot_pairs_repaired"], ["20260312_1515"], "Expected the archived snapshot pair to be repaired.")
    assert_equal(payload["audit"]["warnings"], [], "Expected no warnings after workspace repair.")
    assert_equal(payload["audit"]["errors"], [], "Expected no errors after workspace repair.")

    result = run_python(PAIR_VALIDATOR, [], cwd=project_root)
    assert_contains(result.stdout, "Valid handoff pair", "Expected the repaired live pair to validate.")

    assert_contains(
        active_handover.read_text(encoding="utf-8"),
        "## Session-state pointer\n../session-state/CURRENT.md",
        "Expected the repaired live handover to point back to CURRENT.md with forward slashes.",
    )
    assert_contains(
        archived_handover.read_text(encoding="utf-8"),
        "## Session-state pointer\n../session-state/20260312_1515_session-state.md",
        "Expected the repaired archived handover to point to the archived session snapshot.",
    )
    assert_contains(
        archived_session.read_text(encoding="utf-8"),
        "## Handover pointer\n../handovers/20260312_1515_handover.md",
        "Expected the repaired archived session snapshot to point to the archived handover.",
    )


def test_live_lease_claim_show_and_release(tmp_root: Path) -> None:
    project_root = tmp_root / "lease-manager-project"
    (project_root / ".git").mkdir(parents=True)

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Coordinate live ownership",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--what-was-done",
            "Created the live pair",
            "--last-completed-step",
            "Created the live pair",
            "--current-step",
            "Claiming the lease",
            "--remaining-step",
            "Release the lease",
            "--handover-output",
            "docs/tests/handovers/active_handover.md",
        ],
        cwd=project_root,
    )

    result = run_python(
        LEASE_MANAGER,
        [
            "claim",
            "--holder",
            "codex",
            "--purpose",
            "Editing the live pair",
            "--ttl-minutes",
            "45",
            "--format",
            "json",
        ],
        cwd=project_root,
    )
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "claimed", "Expected the lease claim to succeed.")
    assert_equal(payload["state"], "active", "Expected the claimed lease to be active.")
    assert_equal(payload["holder"], "codex", "Expected the claimed lease holder to be codex.")
    assert_contains(payload["session_state"], "session-state/CURRENT.md", "Expected the lease to point to CURRENT.md.")

    result = run_python(LEASE_MANAGER, ["show", "--format", "json"], cwd=project_root)
    payload = json.loads(result.stdout)
    assert_equal(payload["state"], "active", "Expected lease show to report the active lease.")
    assert_equal(payload["purpose"], "Editing the live pair", "Expected lease show to preserve the purpose.")

    result = run_python(PAIR_SUMMARIZER, ["--format", "json"], cwd=project_root)
    summary = json.loads(result.stdout)
    assert_equal(summary["lease"]["state"], "active", "Expected the summary to expose the active lease.")
    assert_equal(summary["lease"]["holder"], "codex", "Expected the summary to expose the lease holder.")

    result = run_python(WORKSPACE_AUDITOR, ["--format", "json"], cwd=project_root)
    payload = json.loads(result.stdout)
    assert_equal(payload["lease"]["state"], "active", "Expected the workspace audit to expose the active lease.")
    assert_equal(payload["errors"], [], "Expected the active lease to keep the workspace clean.")

    result = run_python(
        LEASE_MANAGER,
        [
            "claim",
            "--holder",
            "other-agent",
            "--purpose",
            "Conflicting edit",
            "--format",
            "json",
        ],
        cwd=project_root,
        expected_returncode=1,
    )
    payload = json.loads(result.stdout)
    assert_contains(
        "\n".join(payload["errors"]),
        "Lease is currently held by codex.",
        "Expected a conflicting lease claim to be rejected.",
    )

    result = run_python(
        LEASE_MANAGER,
        [
            "release",
            "--holder",
            "codex",
            "--format",
            "json",
        ],
        cwd=project_root,
    )
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "released", "Expected the lease release to succeed.")
    assert_equal(payload["state"], "none", "Expected the lease to be gone after release.")

    result = run_python(LEASE_MANAGER, ["show", "--format", "json"], cwd=project_root)
    payload = json.loads(result.stdout)
    assert_equal(payload["state"], "none", "Expected show to report no active lease after release.")


def test_workspace_reporter_aggregates_summary_audit_lease_and_history(tmp_root: Path) -> None:
    project_root = tmp_root / "workspace-reporter-project"
    (project_root / ".git").mkdir(parents=True)

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Aggregate the handoff workspace view",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--what-was-done",
            "Created the live pair",
            "--last-completed-step",
            "Created the live pair",
            "--current-step",
            "Capturing the workspace report",
            "--remaining-step",
            "Review the report",
            "--handover-output",
            "docs/tests/handovers/active_handover.md",
        ],
        cwd=project_root,
    )

    run_python(
        LEASE_MANAGER,
        [
            "claim",
            "--holder",
            "codex",
            "--purpose",
            "Preparing the workspace report",
            "--ttl-minutes",
            "30",
            "--format",
            "json",
        ],
        cwd=project_root,
    )
    run_python(PAIR_ARCHIVER, ["--timestamp", "20260312_1615"], cwd=project_root)

    result = run_python(WORKSPACE_REPORTER, ["--format", "json", "--history-limit", "1"], cwd=project_root)
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "clean", "Expected the workspace report to be clean for a healthy workspace.")
    assert_equal(payload["summary"]["task"], "Aggregate the handoff workspace view", "Expected the report summary to expose the task.")
    assert_equal(payload["summary"]["lease"]["holder"], "codex", "Expected the report summary to expose the lease holder.")
    assert_equal(payload["lease"]["state"], "active", "Expected the top-level report lease to be active.")
    assert_equal(payload["audit"]["result"], "clean", "Expected the report audit block to stay clean.")
    assert_equal(len(payload["history"]["history"]), 1, "Expected the report history to respect the requested limit.")
    assert_equal(payload["history"]["history"][0]["stamp"], "20260312_1615", "Expected the report history to include the archived milestone.")
    assert_equal(payload["warnings"], [], "Expected no report warnings for the healthy workspace.")
    assert_equal(payload["errors"], [], "Expected no report errors for the healthy workspace.")


def test_readiness_checker_classifies_ready_not_ready_and_warning_states(tmp_root: Path) -> None:
    project_root = tmp_root / "readiness-checker-project"
    (project_root / ".git").mkdir(parents=True)

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Gate the handoff transfer",
            "--status",
            "in-progress",
            "--updated-by",
            "codex",
            "--next-owner",
            "qa-reviewer",
            "--what-was-done",
            "Created the live pair",
            "--last-completed-step",
            "Created the live pair",
            "--current-step",
            "Checking readiness",
            "--remaining-step",
            "Transfer to the next operator",
            "--handover-output",
            "docs/tests/handovers/active_handover.md",
        ],
        cwd=project_root,
    )
    docs_root = project_root / "docs" / "tests"

    result = run_python(READINESS_CHECKER, ["--format", "json"], cwd=project_root)
    payload = json.loads(result.stdout)
    assert_equal(payload["verdict"], "ready", "Expected the readiness gate to pass for a healthy workspace.")
    assert_equal(payload["ready"], True, "Expected the healthy workspace to be marked ready.")

    run_python(
        LEASE_MANAGER,
        [
            "claim",
            "--holder",
            "codex",
            "--purpose",
            "Editing before transfer",
            "--ttl-minutes",
            "30",
            "--format",
            "json",
        ],
        cwd=project_root,
    )
    result = run_python(READINESS_CHECKER, ["--format", "json"], cwd=project_root, expected_returncode=1)
    payload = json.loads(result.stdout)
    assert_equal(payload["verdict"], "not-ready", "Expected an active lease to block transfer readiness.")
    assert_contains(
        "\n".join(payload["blocking_reasons"]),
        "Live lease is still active for holder codex.",
        "Expected the readiness gate to explain the active lease blocker.",
    )

    run_python(
        LEASE_MANAGER,
        [
            "release",
            "--holder",
            "codex",
            "--format",
            "json",
        ],
        cwd=project_root,
    )
    orphan_session = docs_root / "session-state" / "20260312_1620_session-state.md"
    shutil.copy2(docs_root / "session-state" / "CURRENT.md", orphan_session)
    replace_section_value(orphan_session, "## Status", "done")
    replace_section_value(orphan_session, "## Last updated", "2026-03-12T16:20:00+01:00")
    replace_section_value(orphan_session, "## Next owner", "None")
    replace_section_value(orphan_session, "## Handover pointer", "None")

    result = run_python(READINESS_CHECKER, ["--format", "json"], cwd=project_root)
    payload = json.loads(result.stdout)
    assert_equal(payload["verdict"], "ready-with-warnings", "Expected non-blocking history drift to downgrade the readiness verdict to warning.")
    assert_equal(payload["ready"], True, "Expected warning-only readiness to remain transferable.")
    assert_contains(
        "\n".join(payload["warnings"]),
        "Snapshot session-state has no timestamp-matched handover snapshot: 20260312_1620_session-state.md",
        "Expected the readiness gate to surface the orphan snapshot warning.",
    )


def test_begin_session_creates_and_resumes_live_work(tmp_root: Path) -> None:
    create_project = tmp_root / "begin-session-create-project"
    (create_project / ".git").mkdir(parents=True)

    result = run_python(
        SESSION_BEGINNER,
        [
            "--holder",
            "codex",
            "--purpose",
            "Investigating login flow",
            "--task",
            "Login flow handoff",
            "--remaining-step",
            "Verify selectors",
            "--file-touched",
            "tests/login.spec.ts",
            "--command-to-resume",
            "npx playwright test tests/login.spec.ts",
            "--format",
            "json",
        ],
        cwd=create_project,
    )
    payload = json.loads(result.stdout)
    assert_equal(payload["action"], "created", "Expected begin session to create the live pair when none exists.")
    assert_equal(payload["status"], "in-progress", "Expected a new session to default to in-progress.")
    assert_equal(payload["next_owner"], "codex", "Expected the holder to become the next owner for a new session.")
    assert_equal(payload["report"]["summary"]["task"], "Login flow handoff", "Expected begin session to persist the task.")
    assert_equal(payload["report"]["summary"]["current_step"], "Investigating login flow", "Expected begin session to default the current step to the purpose.")
    assert_equal(payload["report"]["lease"]["holder"], "codex", "Expected begin session to claim the lease for the holder.")
    assert_contains(payload["session_state"], str(Path("session-state") / "CURRENT.md"), "Expected begin session to create CURRENT.md.")

    update_project = tmp_root / "begin-session-update-project"
    (update_project / ".git").mkdir(parents=True)

    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Checkout flow handoff",
            "--status",
            "not-started",
            "--updated-by",
            "other-agent",
            "--next-owner",
            "other-agent",
            "--current-step",
            "None",
            "--handover-output",
            "docs/tests/handovers/active_handover.md",
        ],
        cwd=update_project,
    )
    run_python(
        LEASE_MANAGER,
        [
            "claim",
            "--holder",
            "other-agent",
            "--purpose",
            "Holding the workspace",
            "--ttl-minutes",
            "30",
            "--format",
            "json",
        ],
        cwd=update_project,
    )

    result = run_python(
        SESSION_BEGINNER,
        [
            "--holder",
            "codex",
            "--purpose",
            "Reviewing checkout flow",
            "--format",
            "json",
        ],
        cwd=update_project,
        expected_returncode=1,
    )
    payload = json.loads(result.stdout)
    assert_contains(
        "\n".join(payload["errors"]),
        "Lease is currently held by other-agent.",
        "Expected begin session to reject a conflicting live lease.",
    )

    result = run_python(
        SESSION_BEGINNER,
        [
            "--holder",
            "codex",
            "--purpose",
            "Reviewing checkout flow",
            "--force-lease",
            "--format",
            "json",
        ],
        cwd=update_project,
    )
    payload = json.loads(result.stdout)
    assert_equal(payload["action"], "updated", "Expected begin session to refresh the existing live pair.")
    assert_equal(payload["status"], "in-progress", "Expected begin session to promote not-started work to in-progress.")
    assert_equal(payload["next_owner"], "codex", "Expected begin session to move ownership to the holder.")
    assert_equal(payload["report"]["summary"]["current_step"], "Reviewing checkout flow", "Expected begin session to refresh the current step from the purpose.")
    assert_equal(payload["report"]["lease"]["holder"], "codex", "Expected begin session to replace the lease holder when forced.")


def test_end_session_releases_lease_and_checks_readiness(tmp_root: Path) -> None:
    project_root = tmp_root / "end-session-project"
    (project_root / ".git").mkdir(parents=True)

    run_python(
        SESSION_BEGINNER,
        [
            "--holder",
            "codex",
            "--purpose",
            "Investigating checkout flow",
            "--task",
            "Checkout flow handoff",
            "--remaining-step",
            "Review the handoff",
            "--format",
            "json",
        ],
        cwd=project_root,
    )

    result = run_python(
        SESSION_ENDER,
        [
            "--holder",
            "codex",
            "--status",
            "ready-for-review",
            "--next-owner",
            "qa-reviewer",
            "--current-step",
            "None",
            "--format",
            "json",
        ],
        cwd=project_root,
    )
    payload = json.loads(result.stdout)
    assert_equal(payload["action"], "updated-and-released", "Expected end session to update the pair and release the lease.")
    assert_equal(payload["status"], "ready-for-review", "Expected end session to persist the provided status.")
    assert_equal(payload["next_owner"], "qa-reviewer", "Expected end session to persist the provided next owner.")
    assert_equal(payload["report"]["lease"]["state"], "none", "Expected the end session wrapper to release the lease.")
    assert_equal(payload["readiness"]["verdict"], "ready", "Expected the workspace to be ready after a clean end session.")
    assert_equal(payload["errors"], [], "Expected no errors for a clean end session.")

    result = run_python(READINESS_CHECKER, ["--format", "json"], cwd=project_root)
    readiness = json.loads(result.stdout)
    assert_equal(readiness["verdict"], "ready", "Expected the explicit readiness check to stay ready after end session.")

    conflict_project = tmp_root / "end-session-conflict-project"
    (conflict_project / ".git").mkdir(parents=True)
    run_python(
        PAIR_GENERATOR,
        [
            "--task",
            "Conflict handoff",
            "--status",
            "in-progress",
            "--updated-by",
            "other-agent",
            "--next-owner",
            "other-agent",
            "--handover-output",
            "docs/tests/handovers/active_handover.md",
        ],
        cwd=conflict_project,
    )
    run_python(
        LEASE_MANAGER,
        [
            "claim",
            "--holder",
            "other-agent",
            "--purpose",
            "Still editing",
            "--ttl-minutes",
            "30",
            "--format",
            "json",
        ],
        cwd=conflict_project,
    )

    result = run_python(
        SESSION_ENDER,
        [
            "--holder",
            "codex",
            "--format",
            "json",
        ],
        cwd=conflict_project,
        expected_returncode=1,
    )
    payload = json.loads(result.stdout)
    assert_contains(
        "\n".join(payload["errors"]),
        "Lease is currently held by other-agent.",
        "Expected end session to reject a conflicting lease holder.",
    )


def test_bundle_exporter_and_importer_move_live_workspace(tmp_root: Path) -> None:
    source_project = tmp_root / "bundle-source-project"
    (source_project / ".git").mkdir(parents=True)
    secret_file = tmp_root / "bundle-signing-secret.txt"
    secret_file.write_text("portable-bundle-secret\n", encoding="utf-8")
    wrong_secret_file = tmp_root / "wrong-bundle-signing-secret.txt"
    wrong_secret_file.write_text("wrong-secret\n", encoding="utf-8")
    ssh_private_key = tmp_root / "bundle_signing_ed25519"
    ssh_public_key, ssh_public_key_fingerprint = generate_ssh_keypair(ssh_private_key, "bundle-signer")

    result = run_python(
        SESSION_BEGINNER,
        [
            "--holder",
            "codex",
            "--purpose",
            "Preparing a portable handoff bundle",
            "--task",
            "Bundle the current handoff state",
            "--remaining-step",
            "Import the bundle into the target workspace",
            "--file-touched",
            "docs/tests/session-state/CURRENT.md",
            "--command-to-resume",
            "python documentation/shared/scripts/import_handoff_bundle.py --bundle portable-handoff.json --format json",
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    begin_payload = json.loads(result.stdout)
    source_handover_name = Path(begin_payload["report"]["summary"]["documents"]["handover"]).name

    bundle_path = tmp_root / "portable-handoff.json"
    result = run_python(
        BUNDLE_EXPORTER,
        [
            "--output",
            str(bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    export_payload = json.loads(result.stdout)
    assert_equal(export_payload["result"], "exported", "Expected exporter to succeed without warnings for a healthy workspace.")
    assert_equal(export_payload["lease_state"], "active", "Expected exporter to preserve the active lease state.")
    assert_equal(export_payload["readiness_verdict"], "not-ready", "Expected exporter to capture the live lease in the readiness verdict.")

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert_equal(bundle["bundle_version"], 2, "Expected exporter to write the current bundle version.")
    assert_equal(bundle["source"]["handover_name"], source_handover_name, "Expected bundle metadata to preserve the live handover filename.")
    assert_equal(bundle["report"]["summary"]["task"], "Bundle the current handoff state", "Expected bundle report metadata to preserve the task.")
    assert_equal(bundle["readiness"]["verdict"], "not-ready", "Expected bundle readiness metadata to preserve the source transfer verdict.")
    assert_equal(bundle["lease"]["inspection"]["holder"], "codex", "Expected bundle lease metadata to preserve the lease holder.")
    assert "integrity" in bundle, "Expected exporter to attach bundle integrity metadata."
    assert "bundle_sha256" in bundle["integrity"], "Expected bundle integrity metadata to include the overall bundle hash."
    assert_equal(bundle["git"]["available"], False, "Expected exporter to fall back cleanly when the temp workspace is not a real git repo.")
    assert_equal(bundle["redaction"]["redaction_count"], 0, "Expected no redactions for the initial bundle content.")

    result = run_python(
        BUNDLE_INSPECTOR,
        [
            "--bundle",
            str(bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    inspection_payload = json.loads(result.stdout)
    assert_equal(
        inspection_payload["result"],
        "valid-with-warnings",
        "Expected bundle inspector to validate the bundle while surfacing the source readiness warning.",
    )
    assert_equal(inspection_payload["task"], "Bundle the current handoff state", "Expected bundle inspector to expose the embedded task.")
    assert_equal(inspection_payload["status"], "in-progress", "Expected bundle inspector to expose the embedded status.")
    assert_equal(inspection_payload["lease_state"], "active", "Expected bundle inspector to expose the embedded lease state.")
    assert_equal(
        inspection_payload["source_readiness_verdict"],
        "not-ready",
        "Expected bundle inspector to expose the exported source readiness verdict.",
    )
    assert_equal(inspection_payload["signature_present"], False, "Expected exported bundles to start unsigned.")
    assert_equal(inspection_payload["git_available"], False, "Expected inspector to expose the git fallback state for non-repo temp workspaces.")
    assert_equal(inspection_payload["redaction_count"], 0, "Expected inspector to expose the redaction count.")
    assert_equal(inspection_payload["redaction_policy_source"], "default", "Expected inspector to expose the default redaction policy source.")

    result = run_python(
        BUNDLE_TRUST_CHECKER,
        [
            "--bundle",
            str(bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
        expected_returncode=1,
    )
    trust_payload = json.loads(result.stdout)
    assert_equal(
        trust_payload["result"],
        "untrusted",
        "Expected the default trust policy to reject an active-work bundle.",
    )
    assert_contains(
        "\n".join(trust_payload["blocking_reasons"]),
        "source readiness verdict 'not-ready'",
        "Expected trust checker to block active-work bundles by default.",
    )
    assert_contains(
        "\n".join(trust_payload["blocking_reasons"]),
        "lease state 'active'",
        "Expected trust checker to block active leases by default.",
    )

    result = run_python(
        BUNDLE_TRUST_CHECKER,
        [
            "--bundle",
            str(bundle_path),
            "--allow-inspection-warnings",
            "--allow-source-not-ready",
            "--allow-active-lease",
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    relaxed_trust_payload = json.loads(result.stdout)
    assert_equal(
        relaxed_trust_payload["result"],
        "trusted-with-warnings",
        "Expected the relaxed trust policy to allow the active-work bundle while preserving warnings.",
    )

    result = run_python(
        BUNDLE_TRUST_CHECKER,
        [
            "--bundle",
            str(bundle_path),
            "--allow-inspection-warnings",
            "--allow-source-not-ready",
            "--allow-active-lease",
            "--require-signature",
            "--secret-file",
            str(secret_file),
            "--format",
            "json",
        ],
        cwd=source_project,
        expected_returncode=1,
    )
    unsigned_signature_trust = json.loads(result.stdout)
    assert_contains(
        "\n".join(unsigned_signature_trust["blocking_reasons"]),
        "bundle is unsigned",
        "Expected signature-required trust checks to reject unsigned bundles.",
    )

    result = run_python(
        BUNDLE_SIGNER,
        [
            "--bundle",
            str(bundle_path),
            "--signer",
            "codex",
            "--key-id",
            "primary",
            "--secret-file",
            str(secret_file),
            "--signed-at",
            "2026-03-13T10:45:00+01:00",
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    sign_payload = json.loads(result.stdout)
    assert_equal(sign_payload["result"], "signed", "Expected bundle signing to succeed.")
    assert_equal(sign_payload["scheme"], "hmac-sha256", "Expected the default bundle signing scheme to remain HMAC.")

    result = run_python(
        BUNDLE_INSPECTOR,
        [
            "--bundle",
            str(bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    signed_inspection_payload = json.loads(result.stdout)
    assert_equal(signed_inspection_payload["signature_present"], True, "Expected the signed bundle to advertise signature metadata.")
    assert_equal(signed_inspection_payload["signature_scheme"], "hmac-sha256", "Expected the inspector to expose the HMAC signature scheme.")
    assert_equal(signed_inspection_payload["signature_signer"], "codex", "Expected the inspector to expose the signature signer.")
    assert_equal(signed_inspection_payload["signature_key_id"], "primary", "Expected the inspector to expose the signature key id.")

    result = run_python(
        BUNDLE_SIGNATURE_VERIFIER,
        [
            "--bundle",
            str(bundle_path),
            "--secret-file",
            str(secret_file),
            "--required-signer",
            "codex",
            "--required-key-id",
            "primary",
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    verify_payload = json.loads(result.stdout)
    assert_equal(verify_payload["result"], "verified", "Expected signature verification to succeed with the correct secret.")

    result = run_python(
        BUNDLE_SIGNATURE_VERIFIER,
        [
            "--bundle",
            str(bundle_path),
            "--secret-file",
            str(wrong_secret_file),
            "--format",
            "json",
        ],
        cwd=source_project,
        expected_returncode=1,
    )
    failed_verify_payload = json.loads(result.stdout)
    assert_contains(
        "\n".join(failed_verify_payload["errors"]),
        "does not match the provided signing secret",
        "Expected verification to fail with the wrong secret.",
    )

    result = run_python(
        BUNDLE_TRUST_CHECKER,
        [
            "--bundle",
            str(bundle_path),
            "--allow-inspection-warnings",
            "--allow-source-not-ready",
            "--allow-active-lease",
            "--require-signature",
            "--allowed-signature-scheme",
            "hmac-sha256",
            "--allowed-signer",
            "codex",
            "--allowed-key-id",
            "primary",
            "--secret-file",
            str(secret_file),
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    signed_trust_payload = json.loads(result.stdout)
    assert_equal(
        signed_trust_payload["result"],
        "trusted-with-warnings",
        "Expected a signed active-work bundle to pass the relaxed signature-aware trust policy.",
    )
    assert_equal(signed_trust_payload["signature_scheme"], "hmac-sha256", "Expected trust evaluation to expose the HMAC signature scheme.")
    assert_equal(signed_trust_payload["signature_verified"], True, "Expected trust evaluation to verify the bundle signature.")

    result = run_python(
        BUNDLE_TRUST_CHECKER,
        [
            "--bundle",
            str(bundle_path),
            "--allow-inspection-warnings",
            "--allow-source-not-ready",
            "--allow-active-lease",
            "--require-signature",
            "--revoked-key-id",
            "primary",
            "--secret-file",
            str(secret_file),
            "--format",
            "json",
        ],
        cwd=source_project,
        expected_returncode=1,
    )
    revoked_payload = json.loads(result.stdout)
    assert_contains(
        "\n".join(revoked_payload["blocking_reasons"]),
        "has been revoked",
        "Expected trust evaluation to reject a revoked signing key id.",
    )

    source_policy_path = source_project / "docs" / "tests" / "handoff-bundle-trust-policy.json"
    source_policy_path.write_text(
        json.dumps(
            {
                "default_profile": "dev",
                "profiles": {
                    "dev": {
                        "allow_inspection_warnings": True,
                        "allow_source_not_ready": True,
                        "allow_active_lease": True,
                        "require_signature": True,
                        "allowed_signature_schemes": ["hmac-sha256"],
                        "allowed_signers": ["codex"],
                        "allowed_key_ids": ["primary"]
                    },
                    "prod": {
                        "require_signature": True,
                        "allowed_signature_schemes": ["sshsig"],
                        "allowed_signers": ["codex"],
                        "allowed_key_ids": ["ssh-primary"],
                        "allowed_public_key_fingerprints": [ssh_public_key_fingerprint]
                    }
                },
                "allow_inspection_warnings": True,
                "allow_source_not_ready": True,
                "allow_active_lease": True,
                "require_signature": True,
                "allowed_signature_schemes": ["hmac-sha256"],
                "allowed_signers": ["codex"],
                "allowed_key_ids": ["primary"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_python(
        BUNDLE_TRUST_CHECKER,
        [
            "--bundle",
            str(bundle_path),
            "--secret-file",
            str(secret_file),
            "--policy-profile",
            "dev",
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    policy_trust_payload = json.loads(result.stdout)
    assert_equal(
        policy_trust_payload["result"],
        "trusted-with-warnings",
        "Expected the checked-in source policy to allow the signed active-work bundle.",
    )
    assert_equal(
        Path(policy_trust_payload["policy_source"]).resolve(),
        source_policy_path.resolve(),
        "Expected trust checker to report the discovered checked-in policy file.",
    )

    invalid_bundle_path = tmp_root / "invalid-portable-handoff.json"
    invalid_bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    invalid_bundle["source"]["handover_name"] = "other_handover.md"
    invalid_bundle_path.write_text(json.dumps(invalid_bundle, indent=2) + "\n", encoding="utf-8")
    result = run_python(
        BUNDLE_INSPECTOR,
        [
            "--bundle",
            str(invalid_bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
        expected_returncode=1,
    )
    invalid_inspection = json.loads(result.stdout)
    assert_contains(
        "\n".join(invalid_inspection["errors"]),
        "Bundle source content hash does not match integrity metadata.",
        "Expected bundle inspector to reject tampered bundle metadata through integrity validation.",
    )

    result = run_python(
        BUNDLE_IMPORTER,
        [
            "--bundle",
            str(invalid_bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
        expected_returncode=1,
    )
    invalid_import = json.loads(result.stdout)
    assert_contains(
        "\n".join(invalid_import["errors"]),
        "Bundle source content hash does not match integrity metadata.",
        "Expected importer to reject tampered bundle metadata through integrity validation.",
    )

    target_project = tmp_root / "bundle-target-project"
    (target_project / ".git").mkdir(parents=True)
    result = run_python(
        BUNDLE_IMPORTER,
        [
            "--bundle",
            str(bundle_path),
            "--trusted-only",
            "--format",
            "json",
        ],
        cwd=target_project,
        expected_returncode=1,
    )
    trusted_only_payload = json.loads(result.stdout)
    assert_contains(
        "\n".join(trusted_only_payload["errors"]),
        "source readiness verdict 'not-ready'",
        "Expected trusted-only import to block an active-work bundle.",
    )

    result = run_python(
        BUNDLE_IMPORTER,
        [
            "--bundle",
            str(bundle_path),
            "--format",
            "json",
        ],
        cwd=target_project,
    )
    import_payload = json.loads(result.stdout)
    assert_equal(
        import_payload["result"],
        "imported-with-warnings",
        "Expected importer to surface the source readiness warning while restoring the live pair.",
    )
    assert_equal(import_payload["status"], "in-progress", "Expected importer to preserve the active status.")
    assert_equal(import_payload["next_owner"], "codex", "Expected importer to preserve the next owner.")
    assert_equal(import_payload["lease_restored"], True, "Expected importer to restore the exported lease context.")
    assert_equal(import_payload["lease_state"], "active", "Expected importer to restore the lease as active.")
    assert_equal(
        import_payload["source_readiness_verdict"],
        "not-ready",
        "Expected importer to surface the exported source readiness verdict.",
    )

    result = run_python(PAIR_VALIDATOR, [], cwd=target_project)
    assert_contains(result.stdout, "Valid handoff pair", "Expected the imported live pair to validate.")

    result = run_python(LEASE_MANAGER, ["show", "--format", "json"], cwd=target_project)
    lease_payload = json.loads(result.stdout)
    assert_equal(lease_payload["state"], "active", "Expected the imported lease to remain active.")
    assert_equal(lease_payload["holder"], "codex", "Expected the imported lease holder to match the bundle.")

    result = run_python(WORKSPACE_REPORTER, ["--format", "json"], cwd=target_project)
    report_payload = json.loads(result.stdout)
    assert_equal(report_payload["summary"]["task"], "Bundle the current handoff state", "Expected the imported workspace report to preserve the task.")

    imported_handover = Path(import_payload["handover"])
    imported_session = Path(import_payload["session_state"])
    imported_handover_text = imported_handover.read_text(encoding="utf-8")
    imported_session_text = imported_session.read_text(encoding="utf-8")
    assert_contains(imported_handover_text, "../session-state/CURRENT.md", "Expected the imported handover to point to the local CURRENT.md file.")
    assert_contains(
        imported_session_text,
        f"../handovers/{source_handover_name}",
        "Expected the imported session-state file to point to the imported handover.",
    )
    if str(source_project) in imported_handover_text or str(source_project) in imported_session_text:
        raise SmokeTestError("Imported documents leaked absolute source workspace paths.")

    run_python(
        SESSION_ENDER,
        [
            "--holder",
            "codex",
            "--status",
            "ready-for-review",
            "--next-owner",
            "qa-reviewer",
            "--current-step",
            "None",
            "--format",
            "json",
        ],
        cwd=source_project,
    )

    signed_ready_bundle_path = tmp_root / "portable-ready-handoff.json"
    run_python(
        BUNDLE_EXPORTER,
        [
            "--output",
            str(signed_ready_bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    run_python(
        BUNDLE_SIGNER,
        [
            "--bundle",
            str(signed_ready_bundle_path),
            "--signer",
            "codex",
            "--key-id",
            "primary",
            "--secret-file",
            str(secret_file),
            "--format",
            "json",
        ],
        cwd=source_project,
    )

    trusted_target_project = tmp_root / "bundle-signed-target-project"
    (trusted_target_project / ".git").mkdir(parents=True)
    trusted_target_policy_path = trusted_target_project / "docs" / "tests" / "handoff-bundle-trust-policy.json"
    trusted_target_policy_path.parent.mkdir(parents=True, exist_ok=True)
    trusted_target_policy_path.write_text(
        json.dumps(
            {
                "require_signature": True,
                "allowed_signers": ["codex"],
                "allowed_key_ids": ["primary"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_python(
        BUNDLE_IMPORTER,
        [
            "--bundle",
            str(signed_ready_bundle_path),
            "--trusted-only",
            "--secret-file",
            str(secret_file),
            "--format",
            "json",
        ],
        cwd=trusted_target_project,
    )
    trusted_import_payload = json.loads(result.stdout)
    assert_equal(
        trusted_import_payload["result"],
        "imported",
        "Expected a ready signed bundle to pass trusted-only import under the checked-in target policy.",
    )
    assert_equal(trusted_import_payload["lease_state"], "none", "Expected the trusted-only signed import to preserve the released lease state.")

    ssh_signed_ready_bundle_path = tmp_root / "portable-ready-handoff-ssh.json"
    run_python(
        BUNDLE_EXPORTER,
        [
            "--output",
            str(ssh_signed_ready_bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    run_python(
        BUNDLE_SIGNER,
        [
            "--bundle",
            str(ssh_signed_ready_bundle_path),
            "--scheme",
            "sshsig",
            "--signer",
            "codex",
            "--key-id",
            "ssh-primary",
            "--private-key-file",
            str(ssh_private_key),
            "--public-key-file",
            str(ssh_public_key),
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    result = run_python(
        BUNDLE_SIGNATURE_VERIFIER,
        [
            "--bundle",
            str(ssh_signed_ready_bundle_path),
            "--required-scheme",
            "sshsig",
            "--required-signer",
            "codex",
            "--required-key-id",
            "ssh-primary",
            "--required-public-key-fingerprint",
            ssh_public_key_fingerprint,
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    ssh_verify_payload = json.loads(result.stdout)
    assert_equal(ssh_verify_payload["result"], "verified", "Expected SSH signature verification to succeed without a shared secret.")
    assert_equal(ssh_verify_payload["scheme"], "sshsig", "Expected the verifier to expose the SSH signature scheme.")
    assert_equal(
        ssh_verify_payload["public_key_fingerprint"],
        ssh_public_key_fingerprint,
        "Expected the verifier to expose the SSH public key fingerprint.",
    )
    result = run_python(
        BUNDLE_TRUST_CHECKER,
        [
            "--bundle",
            str(ssh_signed_ready_bundle_path),
            "--policy-file",
            str(source_policy_path),
            "--policy-profile",
            "prod",
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    ssh_profile_trust_payload = json.loads(result.stdout)
    assert_equal(
        ssh_profile_trust_payload["result"],
        "trusted",
        "Expected the prod trust profile to accept the SSH-signed ready bundle.",
    )

    ssh_signed_target_project = tmp_root / "bundle-ssh-target-project"
    (ssh_signed_target_project / ".git").mkdir(parents=True)
    ssh_target_policy_path = ssh_signed_target_project / "docs" / "tests" / "handoff-bundle-trust-policy.json"
    ssh_target_policy_path.parent.mkdir(parents=True, exist_ok=True)
    ssh_target_policy_path.write_text(
        json.dumps(
            {
                "require_signature": True,
                "allowed_signature_schemes": ["sshsig"],
                "allowed_signers": ["codex"],
                "allowed_key_ids": ["ssh-primary"],
                "allowed_public_key_fingerprints": [ssh_public_key_fingerprint],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_python(
        BUNDLE_IMPORTER,
        [
            "--bundle",
            str(ssh_signed_ready_bundle_path),
            "--trusted-only",
            "--format",
            "json",
        ],
        cwd=ssh_signed_target_project,
    )
    ssh_trusted_import_payload = json.loads(result.stdout)
    assert_equal(
        ssh_trusted_import_payload["result"],
        "imported",
        "Expected a ready SSH-signed bundle to pass trusted-only import under a fingerprint-based policy.",
    )

    preview_target_project = tmp_root / "bundle-preview-target-project"
    (preview_target_project / ".git").mkdir(parents=True)
    preview_policy_path = preview_target_project / "docs" / "tests" / "handoff-bundle-trust-policy.json"
    preview_policy_path.parent.mkdir(parents=True, exist_ok=True)
    preview_policy_path.write_text(
        json.dumps(
            {
                "require_signature": True,
                "allowed_signers": ["codex"],
                "allowed_key_ids": ["primary"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    existing_preview_current = preview_target_project / "docs" / "tests" / "session-state" / "CURRENT.md"
    existing_preview_current.parent.mkdir(parents=True, exist_ok=True)
    existing_preview_current.write_text("# Existing preview file\n", encoding="utf-8")
    result = run_python(
        BUNDLE_IMPORTER,
        [
            "--bundle",
            str(signed_ready_bundle_path),
            "--trusted-only",
            "--secret-file",
            str(secret_file),
            "--dry-run",
            "--format",
            "json",
        ],
        cwd=preview_target_project,
    )
    preview_payload = json.loads(result.stdout)
    assert_equal(preview_payload["result"], "preview-with-warnings", "Expected dry-run import to report overwrite conflicts as warnings.")
    assert_equal(preview_payload["dry_run"], True, "Expected dry-run import to mark the payload as a preview.")
    assert_contains(
        "\n".join(preview_payload["warnings"]),
        "Existing files would block a real import",
        "Expected dry-run preview to report overwrite conflicts without failing.",
    )
    assert_equal(existing_preview_current.read_text(encoding="utf-8"), "# Existing preview file\n", "Expected dry-run import to leave existing files untouched.")

    source_session_path = Path(begin_payload["report"]["summary"]["documents"]["session_state"])
    source_handover_path = Path(begin_payload["report"]["summary"]["documents"]["handover"])
    replace_once(
        source_session_path,
        "python documentation/shared/scripts/import_handoff_bundle.py --bundle portable-handoff.json --format json",
        _ALL_FAKE_TOKENS_COMMAND,
    )
    replace_section_body(
        source_handover_path,
        "## Blockers and decisions",
        "- Authorization: Bearer super-secret-bearer",
    )
    redacted_bundle_path = tmp_root / "portable-redacted-handoff.json"
    result = run_python(
        BUNDLE_EXPORTER,
        [
            "--output",
            str(redacted_bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    redacted_export_payload = json.loads(result.stdout)
    assert_equal(redacted_export_payload["result"], "exported-with-warnings", "Expected secret redaction to be surfaced as an export warning.")
    assert_equal(redacted_export_payload["redaction_count"] != 0, True, "Expected exporter to report redacted values.")
    redacted_bundle = json.loads(redacted_bundle_path.read_text(encoding="utf-8"))
    if "super-secret-token" in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a session-state secret value into the portable bundle.")
    if _FAKE_SLACK_TOKEN in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a Slack-style token into the portable bundle.")
    if _FAKE_OPENAI_KEY in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a Stripe-style token into the portable bundle.")
    if _FAKE_GITLAB_TOKEN in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a GitLab-style token into the portable bundle.")
    if _FAKE_GOOGLE_KEY in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a Google-style API key into the portable bundle.")
    if _FAKE_HF_TOKEN in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a HuggingFace-style token into the portable bundle.")
    if _FAKE_DISCORD_WEBHOOK in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a Discord webhook into the portable bundle.")
    if _FAKE_MAILCHIMP_KEY in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a Mailchimp-style API key into the portable bundle.")
    if _FAKE_SENDGRID_KEY in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a SendGrid-style API key into the portable bundle.")
    if _FAKE_SHOPIFY_TOKEN in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a Shopify admin token into the portable bundle.")
    if _FAKE_TWILIO_KEY in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a Twilio-style API key into the portable bundle.")
    if _FAKE_POSTMAN_KEY in redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Exporter leaked a Postman-style API key into the portable bundle.")
    if "super-secret-bearer" in redacted_bundle["documents"]["handover_markdown"]:
        raise SmokeTestError("Exporter leaked a handover secret value into the portable bundle.")
    assert_contains(
        redacted_bundle["documents"]["session_state_markdown"],
        "[REDACTED]",
        "Expected exporter to redact sensitive material in the exported session-state markdown.",
    )
    assert_contains(
        json.dumps(redacted_bundle["report"]),
        "[REDACTED]",
        "Expected exporter to redact sensitive material in the exported workspace report.",
    )

    replace_section_body(
        source_handover_path,
        "## Blockers and decisions",
        "- Authorization: Bearer visible-because-allowlisted",
    )
    replace_once(
        source_session_path,
        _ALL_FAKE_TOKENS_COMMAND,
        "resume_token=carry-this s3cr3t-literal-value python documentation/shared/scripts/import_handoff_bundle.py --bundle portable-handoff.json --format json",
    )
    redaction_policy_path = source_project / "docs" / "tests" / "handoff-bundle-redaction-policy.json"
    redaction_policy_path.write_text(
        json.dumps(
            {
                "allow_paths": ["bundle.documents.handover_markdown"],
                "deny_paths": ["bundle.source.docs_root"],
                "extra_sensitive_keywords": ["resume_token"],
                "extra_redaction_regexes": ["s3cr3t-[A-Za-z0-9-]+"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    policy_redacted_bundle_path = tmp_root / "portable-policy-redacted-handoff.json"
    result = run_python(
        BUNDLE_EXPORTER,
        [
            "--output",
            str(policy_redacted_bundle_path),
            "--format",
            "json",
        ],
        cwd=source_project,
    )
    policy_redacted_export_payload = json.loads(result.stdout)
    assert_equal(policy_redacted_export_payload["result"], "exported-with-warnings", "Expected policy-driven redaction to still surface export warnings.")
    policy_redacted_bundle = json.loads(policy_redacted_bundle_path.read_text(encoding="utf-8"))
    assert_equal(
        policy_redacted_bundle["redaction"]["policy_source"],
        str(redaction_policy_path.resolve()),
        "Expected the exported bundle to record the checked-in redaction policy source.",
    )
    assert_equal(policy_redacted_bundle["source"]["docs_root"], "[REDACTED]", "Expected deny-path rules to redact explicit bundle paths.")
    if "visible-because-allowlisted" not in policy_redacted_bundle["documents"]["handover_markdown"]:
        raise SmokeTestError("Expected allow-path rules to preserve the allowlisted handover markdown value.")
    if "carry-this" in policy_redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Expected extra sensitive keyword rules to redact the resume token value.")
    if "s3cr3t-literal-value" in policy_redacted_bundle["documents"]["session_state_markdown"]:
        raise SmokeTestError("Expected extra redaction regex rules to redact custom secret literals.")


def test_bundle_trust_policy_generator_and_validator(tmp_root: Path) -> None:
    project_root = tmp_root / "bundle-policy-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(
        BUNDLE_TRUST_POLICY_GENERATOR,
        [
            "--start-dir",
            str(project_root),
            "--require-signature",
            "--allowed-signature-scheme",
            "sshsig",
            "--allowed-signer",
            "codex",
            "--allowed-key-id",
            "primary",
            "--profile-name",
            "dev",
            "--profile-name",
            "prod",
            "--default-profile",
            "dev",
            "--max-age-hours",
            "12",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    payload = json.loads(result.stdout)
    policy_path = Path(payload["policy_path"])
    assert_equal(payload["result"], "generated", "Expected policy generator to create the checked-in trust policy.")
    assert_equal(policy_path.resolve(), (project_root / "docs" / "tests" / "handoff-bundle-trust-policy.json").resolve(), "Expected policy generator to use the deterministic docs root.")
    generated_policy = json.loads(policy_path.read_text(encoding="utf-8"))
    assert_equal(generated_policy["default_profile"], "dev", "Expected generated policies to preserve the default profile.")
    assert_equal(sorted(generated_policy["profiles"].keys()), ["dev", "prod"], "Expected generated policies to include the requested trust profiles.")
    assert_equal(generated_policy["allowed_signature_schemes"], ["sshsig"], "Expected generated policies to include the allowed signature schemes field.")
    assert_equal(generated_policy["revoked_signers"], [], "Expected generated policies to include the revoked signers field.")
    assert_equal(generated_policy["revoked_key_ids"], [], "Expected generated policies to include the revoked key ids field.")
    assert_equal(generated_policy["allowed_public_key_fingerprints"], [], "Expected generated policies to include the allowed public key fingerprints field.")
    assert_equal(generated_policy["revoked_public_key_fingerprints"], [], "Expected generated policies to include the revoked public key fingerprints field.")
    assert_equal(generated_policy["profiles"]["dev"]["require_signature"], False, "Expected the dev profile preset to relax signature requirements.")
    assert_equal(generated_policy["profiles"]["prod"]["require_signature"], True, "Expected the prod profile preset to require signatures.")
    assert_equal(generated_policy["profiles"]["prod"]["allowed_signature_schemes"], ["sshsig"], "Expected the prod profile preset to prefer SSH signatures.")

    result = run_python(
        BUNDLE_TRUST_POLICY_VALIDATOR,
        [
            "--start-dir",
            str(project_root),
            "--profile",
            "prod",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    validation_payload = json.loads(result.stdout)
    assert_equal(validation_payload["result"], "valid", "Expected the generated policy file to validate.")

    policy_data = json.loads(policy_path.read_text(encoding="utf-8"))
    policy_data["unknown_key"] = True
    policy_path.write_text(json.dumps(policy_data, indent=2) + "\n", encoding="utf-8")
    result = run_python(
        BUNDLE_TRUST_POLICY_VALIDATOR,
        [
            "--start-dir",
            str(project_root),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        expected_returncode=1,
    )
    invalid_payload = json.loads(result.stdout)
    assert_contains(
        "\n".join(invalid_payload["errors"]),
        "unknown keys",
        "Expected policy validator to reject unknown keys.",
    )

    second_project = tmp_root / "bundle-policy-template-project"
    (second_project / ".git").mkdir(parents=True)
    result = run_python(
        BUNDLE_TRUST_POLICY_GENERATOR,
        [
            "--start-dir",
            str(second_project),
            "--allowed-signer",
            "release-bot",
            "--profile-name",
            "review",
            "--profile-template",
            "review=staging",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    second_policy_path = Path(json.loads(result.stdout)["policy_path"])
    second_policy = json.loads(second_policy_path.read_text(encoding="utf-8"))
    assert_equal(second_policy["profiles"]["review"]["require_signature"], True, "Expected explicit staging templates to require signatures.")
    assert_equal(second_policy["profiles"]["review"]["allow_active_lease"], False, "Expected explicit staging templates to disallow active leases.")

    override_project = tmp_root / "bundle-policy-override-project"
    (override_project / ".git").mkdir(parents=True)
    result = run_python(
        BUNDLE_TRUST_POLICY_GENERATOR,
        [
            "--start-dir",
            str(override_project),
            "--profile-name",
            "prod",
            "--profile-allowed-signer",
            "prod=release-bot",
            "--profile-max-age-hours",
            "prod=6",
            "--profile-allow-active-lease",
            "prod=true",
            "--profile-signature-secret-env",
            "prod=PROD_HANDOFF_SECRET",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    override_policy_path = Path(json.loads(result.stdout)["policy_path"])
    override_policy = json.loads(override_policy_path.read_text(encoding="utf-8"))
    assert_equal(override_policy["profiles"]["prod"]["allowed_signers"], ["release-bot"], "Expected per-profile allowed signer overrides to be preserved.")
    assert_equal(override_policy["profiles"]["prod"]["max_age_hours"], 6, "Expected per-profile max age overrides to be preserved.")
    assert_equal(override_policy["profiles"]["prod"]["allow_active_lease"], True, "Expected per-profile boolean overrides to be preserved.")
    assert_equal(override_policy["profiles"]["prod"]["signature_secret_env"], "PROD_HANDOFF_SECRET", "Expected per-profile signature secret env overrides to be preserved.")


def test_bundle_ci_policy_generator_and_validator(tmp_root: Path) -> None:
    project_root = tmp_root / "bundle-ci-policy-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(
        BUNDLE_CI_POLICY_GENERATOR,
        [
            "--start-dir",
            str(project_root),
            "--require-portable-bundle-policies",
            "--require-trust-policy",
            "--require-redaction-policy",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    payload = json.loads(result.stdout)
    policy_path = Path(payload["policy_path"])
    assert_equal(payload["result"], "generated", "Expected CI policy generator to create the checked-in CI policy.")
    assert_equal(policy_path.resolve(), (project_root / "docs" / "tests" / "handoff-bundle-ci-policy.json").resolve(), "Expected CI policy generator to use the deterministic docs root.")
    generated_policy = json.loads(policy_path.read_text(encoding="utf-8"))
    assert_equal(generated_policy["require_portable_bundle_policies"], True, "Expected CI policy generator to persist the portable-bundle policy requirement.")
    assert_equal(generated_policy["require_trust_policy"], True, "Expected CI policy generator to persist the trust-policy requirement.")
    assert_equal(generated_policy["require_redaction_policy"], True, "Expected CI policy generator to persist the redaction-policy requirement.")

    result = run_python(
        BUNDLE_CI_POLICY_VALIDATOR,
        [
            "--start-dir",
            str(project_root),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    validation_payload = json.loads(result.stdout)
    assert_equal(validation_payload["result"], "valid", "Expected the generated CI policy file to validate.")

    policy_data = json.loads(policy_path.read_text(encoding="utf-8"))
    policy_data["unexpected_rule"] = True
    policy_path.write_text(json.dumps(policy_data, indent=2) + "\n", encoding="utf-8")
    result = run_python(
        BUNDLE_CI_POLICY_VALIDATOR,
        [
            "--start-dir",
            str(project_root),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        expected_returncode=1,
    )
    invalid_payload = json.loads(result.stdout)
    assert_contains("\n".join(invalid_payload["errors"]), "unknown keys", "Expected CI policy validator to reject unknown keys.")


def test_bundle_redaction_policy_generator_and_validator(tmp_root: Path) -> None:
    project_root = tmp_root / "bundle-redaction-policy-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(
        BUNDLE_REDACTION_POLICY_GENERATOR,
        [
            "--start-dir",
            str(project_root),
            "--allow-redaction-path",
            "bundle.documents.handover_markdown",
            "--deny-redaction-path",
            "bundle.source.docs_root",
            "--extra-sensitive-keyword",
            "resume_token",
            "--extra-redaction-regex",
            "s3cr3t-[A-Za-z0-9-]+",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    payload = json.loads(result.stdout)
    policy_path = Path(payload["policy_path"])
    assert_equal(payload["result"], "generated", "Expected redaction policy generator to create the checked-in redaction policy.")
    assert_equal(policy_path.resolve(), (project_root / "docs" / "tests" / "handoff-bundle-redaction-policy.json").resolve(), "Expected redaction policy generator to use the deterministic docs root.")
    generated_policy = json.loads(policy_path.read_text(encoding="utf-8"))
    assert_equal(generated_policy["allow_paths"], ["bundle.documents.handover_markdown"], "Expected generated redaction policies to preserve allow paths.")
    assert_equal(generated_policy["deny_paths"], ["bundle.source.docs_root"], "Expected generated redaction policies to preserve deny paths.")
    assert_equal(generated_policy["extra_sensitive_keywords"], ["resume_token"], "Expected generated redaction policies to preserve extra keywords.")
    assert_equal(generated_policy["extra_redaction_regexes"], ["s3cr3t-[A-Za-z0-9-]+"], "Expected generated redaction policies to preserve extra regexes.")

    result = run_python(
        BUNDLE_REDACTION_POLICY_VALIDATOR,
        [
            "--start-dir",
            str(project_root),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    validation_payload = json.loads(result.stdout)
    assert_equal(validation_payload["result"], "valid", "Expected the generated redaction policy file to validate.")

    policy_data = json.loads(policy_path.read_text(encoding="utf-8"))
    policy_data["extra_redaction_regexes"] = ["["]
    policy_path.write_text(json.dumps(policy_data, indent=2) + "\n", encoding="utf-8")
    result = run_python(
        BUNDLE_REDACTION_POLICY_VALIDATOR,
        [
            "--start-dir",
            str(project_root),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        expected_returncode=1,
    )
    invalid_payload = json.loads(result.stdout)
    assert_contains(
        "\n".join(invalid_payload["errors"]),
        "Invalid extra redaction regex",
        "Expected redaction policy validator to reject invalid regexes.",
    )


def test_bundle_exporter_captures_git_fingerprint(tmp_root: Path) -> None:
    project_root = tmp_root / "git-fingerprint-project"
    project_root.mkdir(parents=True)
    run_command(["git", "init"], cwd=project_root)

    run_python(
        SESSION_BEGINNER,
        [
            "--holder",
            "codex",
            "--purpose",
            "Preparing git fingerprint coverage",
            "--task",
            "Capture git context in bundle exports",
            "--remaining-step",
            "Inspect the exported bundle",
            "--format",
            "json",
        ],
        cwd=project_root,
    )

    run_command(["git", "add", "."], cwd=project_root)
    run_command(
        [
            "git",
            "-c",
            "user.name=Smoke Test",
            "-c",
            "user.email=smoke@example.com",
            "commit",
            "-m",
            "Initial handoff state",
        ],
        cwd=project_root,
    )

    current_state = project_root / "docs" / "tests" / "session-state" / "CURRENT.md"
    replace_once(current_state, "## Current step\nPreparing git fingerprint coverage", "## Current step\nDirty workspace after commit")

    bundle_path = tmp_root / "git-fingerprint-bundle.json"
    result = run_python(
        BUNDLE_EXPORTER,
        [
            "--output",
            str(bundle_path),
            "--format",
            "json",
        ],
        cwd=project_root,
    )
    export_payload = json.loads(result.stdout)
    assert_equal(export_payload["git_available"], True, "Expected exporter to detect the initialized git repository.")
    assert_equal(export_payload["git_dirty"], True, "Expected exporter to mark the modified repo as dirty.")

    result = run_python(
        BUNDLE_INSPECTOR,
        [
            "--bundle",
            str(bundle_path),
            "--format",
            "json",
        ],
        cwd=project_root,
    )
    inspection_payload = json.loads(result.stdout)
    assert_equal(inspection_payload["git_available"], True, "Expected inspector to expose git metadata for a real git repo.")
    assert_equal(inspection_payload["git_dirty"], True, "Expected inspector to expose the dirty repo state.")
    if inspection_payload["git_dirty_fingerprint"] in {"clean", "None", "unknown"}:
        raise SmokeTestError("Expected a dirty git fingerprint for a modified git repository export.")
    if inspection_payload["git_status_fingerprint"] in {"clean", "None", "unknown"}:
        raise SmokeTestError("Expected a status fingerprint for a modified git repository export.")
    if inspection_payload["git_patch_summary_fingerprint"] in {"clean", "None", "unknown"}:
        raise SmokeTestError("Expected a patch summary fingerprint for a modified git repository export.")
    if inspection_payload["git_changed_file_count"] <= 0:
        raise SmokeTestError("Expected the inspector to expose a positive changed file count for a modified git repository export.")
    if inspection_payload["git_added_line_count"] <= 0:
        raise SmokeTestError("Expected the inspector to expose positive added line counts for a modified git repository export.")


def test_handoff_ci_runner_passes_in_skip_smoke_mode(tmp_root: Path) -> None:
    project_root = tmp_root / "handoff-ci-project"
    (project_root / ".git").mkdir(parents=True)

    run_python(
        BUNDLE_TRUST_POLICY_GENERATOR,
        [
            "--start-dir",
            str(project_root),
            "--require-signature",
            "--allowed-signer",
            "codex",
            "--allowed-key-id",
            "primary",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    run_python(
        BUNDLE_CI_POLICY_GENERATOR,
        [
            "--start-dir",
            str(project_root),
            "--require-portable-bundle-policies",
            "--require-trust-policy",
            "--require-redaction-policy",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    run_python(
        BUNDLE_REDACTION_POLICY_GENERATOR,
        [
            "--start-dir",
            str(project_root),
            "--deny-redaction-path",
            "bundle.source.docs_root",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )

    result = run_python(
        CI_CHECK_RUNNER,
        [
            "--start-dir",
            str(project_root),
            "--skip-smoke",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "ok", "Expected the CI runner to pass in skip-smoke mode for a valid checked-in policy.")
    checks = {check["name"]: check["result"] for check in payload["checks"]}
    assert_equal(checks["py_compile"], "passed", "Expected the CI runner to compile the shared scripts.")
    assert_equal(checks["trust_policy"], "passed", "Expected the CI runner to validate the checked-in policy.")
    assert_equal(checks["redaction_policy"], "passed", "Expected the CI runner to validate the checked-in redaction policy.")
    assert_equal(checks["ci_policy"], "passed", "Expected the CI runner to validate the checked-in CI policy.")
    assert_equal(checks["smoke"], "skipped", "Expected the CI runner to skip the smoke suite when requested.")


def test_handoff_ci_runner_enforces_required_policy_files(tmp_root: Path) -> None:
    project_root = tmp_root / "handoff-ci-required-policy-project"
    (project_root / ".git").mkdir(parents=True)
    ci_policy_path = project_root / "docs" / "tests" / "handoff-bundle-ci-policy.json"
    ci_policy_path.parent.mkdir(parents=True, exist_ok=True)
    ci_policy_path.write_text(
        json.dumps(
            {
                "require_portable_bundle_policies": True,
                "require_trust_policy": True,
                "require_redaction_policy": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_python(
        CI_CHECK_RUNNER,
        [
            "--start-dir",
            str(project_root),
            "--skip-smoke",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        expected_returncode=1,
    )
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "error", "Expected the CI runner to fail when required checked-in policy files are missing.")
    assert_contains("\n".join(payload["errors"]), "required policy file is missing", "Expected CI enforcement to report missing required policy files.")


def test_handoff_ci_runner_can_require_ci_policy_file(tmp_root: Path) -> None:
    project_root = tmp_root / "handoff-ci-missing-ci-policy-project"
    (project_root / ".git").mkdir(parents=True)

    result = run_python(
        CI_CHECK_RUNNER,
        [
            "--start-dir",
            str(project_root),
            "--require-ci-policy",
            "--skip-smoke",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        expected_returncode=1,
    )
    payload = json.loads(result.stdout)
    assert_equal(payload["result"], "error", "Expected the CI runner to fail when the CI policy file is required but missing.")
    assert_contains("\n".join(payload["errors"]), "ci_policy failed: required policy file is missing", "Expected CI enforcement to report missing CI policy files.")


def test_agent_metadata_advertises_current_lifecycle() -> None:
    handover_text = HANDOVER_AGENT_METADATA.read_text(encoding="utf-8")
    assert_contains(handover_text, 'display_name: "Handover"', "Expected handover metadata to expose the display name.")
    assert_contains(
        handover_text,
        'short_description: "Begin, end, assess, inspect, sign, verify, trust, repair, report, export, and import handoffs"',
        "Expected handover metadata to advertise the current lifecycle.",
    )
    assert_contains(
        handover_text,
        'default_prompt: "Use $handover to begin, end, assess, inspect, sign, verify, trust, report, repair, update, validate, summarize, archive, restore, export, or import the current Playwright handoff for this task."',
        "Expected handover metadata to preserve the literal $handover prompt token.",
    )

    session_text = SESSION_AGENT_METADATA.read_text(encoding="utf-8")
    assert_contains(session_text, 'display_name: "Session State"', "Expected session-state metadata to expose the display name.")
    assert_contains(
        session_text,
        'short_description: "Begin, end, assess, inspect, sign, verify, trust, repair, report, export, and import session state"',
        "Expected session-state metadata to advertise the current lifecycle.",
    )
    assert_contains(
        session_text,
        'default_prompt: "Use $session-state to begin, end, assess, inspect, sign, verify, trust, report, repair, update, validate, summarize, archive, restore, export, or import the live Playwright resume state for this task."',
        "Expected session-state metadata to preserve the literal $session-state prompt token.",
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="handoff-smoke-") as tmp_dir_name:
        tmp_root = Path(tmp_dir_name)
        test_agent_metadata_advertises_current_lifecycle()
        test_default_root_and_link_validation(tmp_root)
        test_existing_root_preferred(tmp_root)
        test_done_session_preserves_explicit_handover_pointer(tmp_root)
        test_pair_generator_creates_consistent_pair(tmp_root)
        test_pair_updater_preserves_and_syncs_pair(tmp_root)
        test_latest_pair_resolver_and_zero_arg_tools(tmp_root)
        test_latest_pair_resolver_without_current(tmp_root)
        test_pair_archiver_creates_snapshot_pair(tmp_root)
        test_pair_history_without_current(tmp_root)
        test_pair_restorer_reactivates_archived_snapshot(tmp_root)
        test_workspace_auditor_reports_clean_warnings_and_errors(tmp_root)
        test_workspace_repairer_fixes_live_and_snapshot_drift(tmp_root)
        test_live_lease_claim_show_and_release(tmp_root)
        test_workspace_reporter_aggregates_summary_audit_lease_and_history(tmp_root)
        test_readiness_checker_classifies_ready_not_ready_and_warning_states(tmp_root)
        test_begin_session_creates_and_resumes_live_work(tmp_root)
        test_end_session_releases_lease_and_checks_readiness(tmp_root)
        test_bundle_trust_policy_generator_and_validator(tmp_root)
        test_bundle_ci_policy_generator_and_validator(tmp_root)
        test_bundle_redaction_policy_generator_and_validator(tmp_root)
        test_bundle_exporter_and_importer_move_live_workspace(tmp_root)
        test_bundle_exporter_captures_git_fingerprint(tmp_root)
        test_handoff_ci_runner_passes_in_skip_smoke_mode(tmp_root)
        test_handoff_ci_runner_enforces_required_policy_files(tmp_root)
        test_handoff_ci_runner_can_require_ci_policy_file(tmp_root)

    print("Smoke test passed: handoff workflow scripts generated, linked, validated, and rejected invalid states correctly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
