#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_RELATIVE_ROOT = Path("docs") / "tests"
EXISTING_CANDIDATES = (
    Path("docs") / "tests",
    Path("docs") / "test",
    Path("test-docs"),
    Path("test-documentation"),
)


def find_project_root(start_dir: Path) -> Path:
    start_dir = start_dir.resolve()
    for candidate in (start_dir, *start_dir.parents):
        if (candidate / ".git").exists():
            return candidate
    return start_dir


def resolve_docs_root(start_dir: Path | None = None, explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()

    project_root = find_project_root(start_dir or Path.cwd())
    for relative_candidate in EXISTING_CANDIDATES:
        candidate = project_root / relative_candidate
        if candidate.exists():
            return candidate.resolve()

    return (project_root / DEFAULT_RELATIVE_ROOT).resolve()


def ensure_dirs(root: Path, ensure: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    if ensure in {"handover", "both"}:
        (root / "handovers").mkdir(parents=True, exist_ok=True)
    if ensure in {"session-state", "both"}:
        (root / "session-state").mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve the deterministic test documentation root.")
    parser.add_argument("--start-dir", help="Directory to start project-root discovery from. Defaults to the current working directory.")
    parser.add_argument("--root", help="Explicit documentation root. Overrides discovery.")
    parser.add_argument(
        "--ensure",
        choices=("none", "handover", "session-state", "both"),
        default="none",
        help="Create the root and selected child directories.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve() if args.start_dir else Path.cwd()
    root = resolve_docs_root(start_dir=start_dir, explicit_root=args.root)
    if args.ensure != "none":
        ensure_dirs(root, args.ensure)
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
