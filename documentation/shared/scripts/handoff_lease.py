#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_SCRIPTS = REPO_ROOT / "documentation" / "shared" / "scripts"
HANDOVER_SCRIPTS = REPO_ROOT / "documentation" / "handover" / "scripts"
SESSION_SCRIPTS = REPO_ROOT / "documentation" / "session-state" / "scripts"

for script_dir in (SHARED_SCRIPTS, HANDOVER_SCRIPTS, SESSION_SCRIPTS):
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

from resolve_latest_handoff_pair import HANDOVER_NAME_RE, resolve_latest_pair  # type: ignore  # noqa: E402
from resolve_test_docs_root import resolve_docs_root  # type: ignore  # noqa: E402
from validate_handover import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as HANDOVER_ROOT,
    extract_pointer as extract_handover_pointer,
    parse_sections as parse_handover_sections,
    resolve_pointer as resolve_handover_pointer,
)
from validate_session_state import (  # type: ignore  # noqa: E402
    REQUIRED_ROOT as SESSION_ROOT,
    extract_pointer as extract_session_pointer,
    parse_sections as parse_session_sections,
    resolve_pointer as resolve_session_pointer,
)


LEASE_FILENAME = "ACTIVE_LEASE.json"
LEASE_VERSION = 1


def current_timestamp() -> datetime:
    return datetime.now().astimezone()


def format_timestamp(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Lease timestamps must include a timezone offset.")
    return parsed


def lease_path_for_docs_root(docs_root: Path) -> Path:
    return docs_root / "session-state" / LEASE_FILENAME


def relative_pointer(from_path: Path, to_path: Path) -> str:
    return Path(os.path.relpath(to_path.resolve(), start=from_path.resolve())).as_posix()


def resolve_docs_pointer(docs_root: Path, pointer: str) -> Path:
    path = Path(pointer.replace("\\", "/"))
    if path.is_absolute():
        return path.resolve()
    return (docs_root / path).resolve()


def resolve_live_pair(start_dir: Path, explicit_root: str | None = None) -> tuple[Path, Path, Path, str]:
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=explicit_root)
    current_session = (docs_root / "session-state" / "CURRENT.md").resolve()
    handover_dir = docs_root / "handovers"

    if current_session.exists():
        try:
            session_root, session_sections, _ = parse_session_sections(current_session.read_text(encoding="utf-8"))
            if session_root == SESSION_ROOT:
                pointer = extract_session_pointer(session_sections)
                if pointer is not None:
                    linked_handover = resolve_session_pointer(current_session, pointer)
                    if linked_handover.exists():
                        return docs_root, linked_handover.resolve(), current_session, "current-pointer"
        except Exception:
            pass

        for handover_path in sorted(handover_dir.glob("*.md")):
            handover_path = handover_path.resolve()
            try:
                handover_root, handover_sections, _ = parse_handover_sections(handover_path.read_text(encoding="utf-8"))
                if handover_root != HANDOVER_ROOT:
                    continue
                pointer = extract_handover_pointer(handover_sections)
                if pointer is None:
                    continue
                linked_session = resolve_handover_pointer(handover_path, pointer)
                if linked_session.resolve() == current_session:
                    return docs_root, handover_path, current_session, "back-pointer-scan"
            except Exception:
                continue

        non_timestamped = [
            path.resolve()
            for path in sorted(handover_dir.glob("*.md"))
            if HANDOVER_NAME_RE.fullmatch(path.name) is None
        ]
        if len(non_timestamped) == 1:
            return docs_root, non_timestamped[0], current_session, "current-plus-single-live-handover"

    docs_root, handover_path, session_path, source = resolve_latest_pair(start_dir=start_dir, explicit_root=explicit_root)
    return docs_root, handover_path, session_path, source


def load_lease_file(lease_path: Path) -> dict[str, object] | None:
    if not lease_path.exists():
        return None
    return json.loads(lease_path.read_text(encoding="utf-8"))


def build_lease_payload(
    docs_root: Path,
    holder: str,
    purpose: str,
    handover_path: Path,
    session_path: Path,
    ttl_minutes: int,
) -> dict[str, object]:
    now = current_timestamp()
    expires_at = now + timedelta(minutes=ttl_minutes)
    return {
        "version": LEASE_VERSION,
        "holder": holder,
        "purpose": purpose,
        "acquired_at": format_timestamp(now),
        "expires_at": format_timestamp(expires_at),
        "handover": relative_pointer(docs_root, handover_path),
        "session_state": relative_pointer(docs_root, session_path),
    }


def validate_lease_payload(docs_root: Path, payload: dict[str, object]) -> tuple[list[str], list[str], dict[str, object]]:
    errors: list[str] = []
    warnings: list[str] = []
    normalized = dict(payload)

    version = payload.get("version")
    if version != LEASE_VERSION:
        errors.append(f"Lease version must be {LEASE_VERSION}.")

    holder = str(payload.get("holder", "")).strip()
    if not holder:
        errors.append("Lease holder is required.")
    normalized["holder"] = holder or "None"

    purpose = str(payload.get("purpose", "")).strip()
    if not purpose:
        errors.append("Lease purpose is required.")
    normalized["purpose"] = purpose or "None"

    acquired_at_raw = str(payload.get("acquired_at", "")).strip()
    expires_at_raw = str(payload.get("expires_at", "")).strip()
    acquired_at = None
    expires_at = None
    if not acquired_at_raw:
        errors.append("Lease acquired_at is required.")
    else:
        try:
            acquired_at = parse_timestamp(acquired_at_raw)
        except ValueError as exc:
            errors.append(str(exc))
    if not expires_at_raw:
        errors.append("Lease expires_at is required.")
    else:
        try:
            expires_at = parse_timestamp(expires_at_raw)
        except ValueError as exc:
            errors.append(str(exc))

    if acquired_at is not None and expires_at is not None and expires_at <= acquired_at:
        errors.append("Lease expires_at must be later than acquired_at.")

    handover_pointer = str(payload.get("handover", "")).strip()
    session_pointer = str(payload.get("session_state", "")).strip()
    if not handover_pointer:
        errors.append("Lease handover pointer is required.")
    if not session_pointer:
        errors.append("Lease session_state pointer is required.")
    if "\\" in handover_pointer:
        errors.append("Lease handover pointer must use forward slashes.")
    if "\\" in session_pointer:
        errors.append("Lease session_state pointer must use forward slashes.")
    normalized["handover"] = handover_pointer
    normalized["session_state"] = session_pointer

    handover_path = None
    session_path = None
    if handover_pointer:
        handover_path = resolve_docs_pointer(docs_root, handover_pointer)
        if not handover_path.exists():
            errors.append(f"Lease handover pointer does not exist: {handover_pointer}")
    if session_pointer:
        session_path = resolve_docs_pointer(docs_root, session_pointer)
        if not session_path.exists():
            errors.append(f"Lease session_state pointer does not exist: {session_pointer}")

    now = current_timestamp()
    state = "invalid"
    if not errors:
        if expires_at is not None and expires_at <= now:
            state = "expired"
        else:
            state = "active"
        if session_path is not None and session_path.name != "CURRENT.md":
            warnings.append("Lease session_state pointer does not target CURRENT.md.")

        try:
            _, live_handover, live_session, _ = resolve_live_pair(start_dir=docs_root, explicit_root=str(docs_root))
        except Exception:
            live_handover = None
            live_session = None
        if live_handover is not None and live_session is not None:
            if handover_path is not None and handover_path.resolve() != live_handover.resolve():
                warnings.append("Lease handover pointer does not match the current live handover.")
            if session_path is not None and session_path.resolve() != live_session.resolve():
                warnings.append("Lease session_state pointer does not match the current live session-state file.")

    normalized["state"] = state
    normalized["lease_path"] = str(lease_path_for_docs_root(docs_root))
    normalized["docs_root"] = str(docs_root)
    return errors, warnings, normalized


def inspect_lease(start_dir: Path, explicit_root: str | None = None) -> dict[str, object]:
    docs_root = resolve_docs_root(start_dir=start_dir, explicit_root=explicit_root)
    lease_path = lease_path_for_docs_root(docs_root)
    payload = {
        "docs_root": str(docs_root),
        "lease_path": str(lease_path),
        "exists": lease_path.exists(),
        "state": "none",
        "holder": "None",
        "purpose": "None",
        "acquired_at": "None",
        "expires_at": "None",
        "handover": "None",
        "session_state": "None",
        "warnings": [],
        "errors": [],
    }
    if not lease_path.exists():
        return payload

    try:
        raw_payload = load_lease_file(lease_path)
    except json.JSONDecodeError as exc:
        payload["state"] = "invalid"
        payload["errors"] = [f"Lease file is not valid JSON: {exc}"]
        return payload

    assert raw_payload is not None
    errors, warnings, normalized = validate_lease_payload(docs_root, raw_payload)
    payload.update(normalized)
    payload["exists"] = True
    payload["warnings"] = warnings
    payload["errors"] = errors
    return payload
