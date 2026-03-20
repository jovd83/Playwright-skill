from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
NAME_PATTERN = re.compile(r"^[a-z0-9-]{1,64}$")
LINK_PATTERN = re.compile(r"(?<!\!)\[[^\]]+\]\(([^)]+)\)")
FENCED_CODE_PATTERN = re.compile(r"```.*?```", re.DOTALL)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter opening delimiter")

    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter block is not closed")

    raw = parts[1].strip().splitlines()
    data: dict[str, str] = {}
    for line in raw:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def parse_openai_yaml(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8").splitlines()
    if not text or text[0].strip() != "interface:":
        raise ValueError("agents/openai.yaml must start with 'interface:'")

    data: dict[str, str] = {}
    for line in text[1:]:
        if not line.strip():
            continue
        if not line.startswith("  ") or ":" not in line:
            raise ValueError(f"invalid openai.yaml line: {line!r}")
        key, value = line.strip().split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def validate_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    text = FENCED_CODE_PATTERN.sub("", text)
    for target in LINK_PATTERN.findall(text):
        target = target.strip()
        if not target or target.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue

        location = target.split("#", 1)[0]
        resolved = (path.parent / location).resolve()
        if not resolved.exists():
            errors.append(f"{path.relative_to(REPO_ROOT)}: broken link target '{target}'")


def main() -> int:
    errors: list[str] = []

    skill_files = sorted(REPO_ROOT.rglob("SKILL.md"))
    if not skill_files:
        errors.append("no SKILL.md files found")

    seen_names: set[str] = set()
    for skill_file in skill_files:
        try:
            frontmatter = parse_frontmatter(skill_file)
        except ValueError as exc:
            errors.append(f"{skill_file.relative_to(REPO_ROOT)}: {exc}")
            continue

        keys = set(frontmatter)
        allowed_keys = {"name", "description"}
        if keys != allowed_keys:
            extra = sorted(keys - allowed_keys)
            missing = sorted(allowed_keys - keys)
            if extra:
                errors.append(
                    f"{skill_file.relative_to(REPO_ROOT)}: unsupported frontmatter keys {extra}"
                )
            if missing:
                errors.append(
                    f"{skill_file.relative_to(REPO_ROOT)}: missing frontmatter keys {missing}"
                )

        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")
        if not name or not NAME_PATTERN.match(name):
            errors.append(
                f"{skill_file.relative_to(REPO_ROOT)}: invalid skill name '{name}'"
            )
        if name in seen_names:
            errors.append(
                f"{skill_file.relative_to(REPO_ROOT)}: duplicate skill name '{name}'"
            )
        seen_names.add(name)

        if not description:
            errors.append(f"{skill_file.relative_to(REPO_ROOT)}: empty description")

        validate_links(skill_file, errors)

    for skill_file in skill_files:
        metadata_path = skill_file.parent / "agents" / "openai.yaml"
        if not metadata_path.exists():
            errors.append(f"{metadata_path.relative_to(REPO_ROOT)}: missing skill metadata")
            continue
        try:
            metadata = parse_openai_yaml(metadata_path)
        except ValueError as exc:
            errors.append(f"{metadata_path.relative_to(REPO_ROOT)}: {exc}")
            continue

        required_fields = {"display_name", "short_description", "default_prompt"}
        missing_fields = sorted(required_fields - set(metadata))
        if missing_fields:
            errors.append(
                f"{metadata_path.relative_to(REPO_ROOT)}: missing interface fields {missing_fields}"
            )

    for doc_path in [
        REPO_ROOT / "README.md",
        REPO_ROOT / "CONTRIBUTING.md",
        REPO_ROOT / "CHANGELOG.md",
        REPO_ROOT / "reports" / "skill-inventory.md",
    ]:
        if doc_path.exists():
            validate_links(doc_path, errors)

    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Repository validation passed for {len(skill_files)} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
