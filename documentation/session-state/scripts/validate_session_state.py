#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import re
from pathlib import Path
import sys


VALID_STATUSES = {"not-started", "in-progress", "blocked", "ready-for-review", "done"}
REQUIRED_ROOT = "# Session State"
REQUIRED_SECTIONS = [
    "Task",
    "Status",
    "Last updated",
    "Updated by",
    "Next owner",
    "Last completed step",
    "Current step",
    "Remaining steps",
    "Blockers",
    "Decisions and assumptions",
    "Files touched",
    "Commands to resume",
    "Validation snapshot",
    "Artifacts",
    "Handover pointer",
]
SCALAR_SECTIONS = {
    "Task",
    "Status",
    "Last updated",
    "Updated by",
    "Next owner",
    "Last completed step",
    "Current step",
    "Handover pointer",
}


def parse_sections(text: str) -> tuple[str | None, dict[str, str], list[str]]:
    lines = text.splitlines()
    root_heading = next((line.strip() for line in lines if line.strip()), None)
    sections: dict[str, list[str]] = {}
    section_order: list[str] = []
    current: str | None = None

    for line in lines:
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            section_order.append(current)
            continue
        if current is not None:
            sections[current].append(line.rstrip())

    return root_heading, {name: "\n".join(content).strip() for name, content in sections.items()}, section_order


def first_meaningful_line(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        return line
    return ""


def raw_first_meaningful_line(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        return line
    return ""


def normalize_value(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1]
    if value.startswith("<") and value.endswith(">") and len(value) >= 2:
        value = value[1:-1]
    markdown_link = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", value)
    if markdown_link:
        value = markdown_link.group(1).strip()
    return value.strip()


def looks_like_placeholder(value: str) -> bool:
    stripped = value.strip()
    if stripped.startswith("<") and stripped.endswith(">") and len(stripped) >= 2:
        return True
    return stripped.lower() in {"todo", "tbd", "placeholder"}


def extract_status(sections: dict[str, str]) -> str:
    return normalize_value(first_meaningful_line(sections["Status"]))


def extract_last_updated(sections: dict[str, str]) -> str:
    return normalize_value(first_meaningful_line(sections["Last updated"]))


def extract_updated_by(sections: dict[str, str]) -> str:
    return normalize_value(first_meaningful_line(sections["Updated by"]))


def extract_next_owner(sections: dict[str, str]) -> str:
    return normalize_value(first_meaningful_line(sections["Next owner"]))


def extract_pointer(sections: dict[str, str]) -> str | None:
    pointer = normalize_value(first_meaningful_line(sections["Handover pointer"]))
    if not pointer or pointer.lower() == "none":
        return None
    return pointer


def pointer_uses_backslashes(pointer: str) -> bool:
    return "\\" in pointer


def resolve_pointer(document_path: Path, pointer: str) -> Path:
    path = Path(pointer.replace("\\", "/"))
    if path.is_absolute():
        return path
    return (document_path.parent / path).resolve()


def extract_status_from_linked_file(path: Path, expected_root: str) -> str:
    text = path.read_text(encoding="utf-8")
    root_heading, sections, _ = parse_sections(text)
    if root_heading != expected_root:
        raise ValueError(f"Linked file has unexpected root heading: {root_heading!r}")
    if "Status" not in sections:
        raise ValueError("Linked file is missing the Status section.")
    status = normalize_value(first_meaningful_line(sections["Status"]))
    if status not in VALID_STATUSES:
        raise ValueError(f"Linked file has invalid status: {status!r}")
    return status


def validate_document(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    root_heading, sections, section_order = parse_sections(text)

    if root_heading != REQUIRED_ROOT:
        errors.append(f"Expected first heading {REQUIRED_ROOT!r}, found {root_heading!r}.")

    if section_order != REQUIRED_SECTIONS:
        errors.append("Section order does not match the required session-state template order.")

    for section in REQUIRED_SECTIONS:
        if section not in sections:
            errors.append(f"Missing required section: {section}.")
            continue
        if not sections[section].strip():
            errors.append(f"Section is empty: {section}.")
            continue
        if section in SCALAR_SECTIONS and looks_like_placeholder(raw_first_meaningful_line(sections[section])):
            errors.append(f"Section still contains an unresolved placeholder: {section}.")

    if errors:
        return errors

    status = extract_status(sections)
    if status not in VALID_STATUSES:
        errors.append(f"Invalid status: {status!r}.")

    last_updated = extract_last_updated(sections)
    try:
        parsed_last_updated = datetime.fromisoformat(last_updated)
    except ValueError:
        errors.append(f"Invalid Last updated timestamp: {last_updated!r}.")
    else:
        if "T" not in last_updated:
            errors.append("Last updated must include date and time.")
        if parsed_last_updated.tzinfo is None or parsed_last_updated.utcoffset() is None:
            errors.append("Last updated must include a timezone offset.")

    updated_by = extract_updated_by(sections)
    if not updated_by or updated_by.lower() == "none":
        errors.append("Updated by must identify the last human or AI editor.")

    next_owner = extract_next_owner(sections)
    if status == "done":
        if next_owner != "None":
            errors.append("Next owner must be `None` when status is done.")
    elif not next_owner or next_owner.lower() == "none":
        errors.append("Non-done session-state files must identify the next owner.")

    pointer = extract_pointer(sections)
    if pointer is not None:
        if pointer_uses_backslashes(pointer):
            errors.append("Handover pointer must use forward slashes.")
        linked_path = resolve_pointer(path, pointer)
        if not linked_path.exists():
            errors.append(f"Handover pointer does not exist: {pointer}")
        else:
            try:
                linked_status = extract_status_from_linked_file(linked_path, "# Handover")
            except ValueError as exc:
                errors.append(str(exc))
            else:
                if linked_status != status:
                    errors.append(
                        f"Status mismatch between session-state ({status}) and linked handover ({linked_status})."
                    )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a session-state markdown file.")
    parser.add_argument("path", help="Path to the session-state markdown file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    if not path.exists():
        print(f"File does not exist: {path}", file=sys.stderr)
        return 1

    errors = validate_document(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Valid session-state file: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
