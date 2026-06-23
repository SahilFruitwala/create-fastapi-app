"""create-fastapi-app — scaffold a FastAPI + SQLAlchemy + Alembic backend."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import templates

MANAGERS = ["uv", "pdm", "pip"]


def _prompt(text: str, default: str) -> str:
    try:
        value = input(f"{text} [{default}]: ").strip()
    except EOFError:
        return default
    return value or default


def _prompt_manager() -> str:
    print("Package manager:")
    print("  1) uv     (fast, recommended)")
    print("  2) pdm")
    print("  3) pip + .venv")
    while True:
        try:
            choice = input("Choose [1]: ").strip() or "1"
        except EOFError:
            return "uv"
        mapping = {"1": "uv", "2": "pdm", "3": "pip",
                   "uv": "uv", "pdm": "pdm", "pip": "pip"}
        if choice in mapping:
            return mapping[choice]
        print("Please enter 1, 2, or 3.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="create-fastapi-app",
        description="Scaffold a FastAPI + SQLAlchemy (async) + Alembic backend.",
    )
    parser.add_argument("name", nargs="?", help="project directory name")
    parser.add_argument(
        "-p", "--package-manager", choices=MANAGERS,
        help="dependency manager to target (uv, pdm, or pip)",
    )
    parser.add_argument(
        "-d", "--package-dir",
        help="name of the Python package / code directory (default: app)",
    )
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="accept defaults without prompting",
    )
    args = parser.parse_args(argv)

    interactive = sys.stdin.isatty() and not args.yes

    name = args.name or (_prompt("Project name", "myapp") if interactive else "myapp")

    pkg = args.package_dir or (
        _prompt("Main code/package directory", "app") if interactive else "app"
    )
    if not pkg.isidentifier():
        parser.error(f"package dir '{pkg}' is not a valid Python identifier")

    manager = args.package_manager or (
        _prompt_manager() if interactive else "uv"
    )

    target = Path(name)
    if target.exists():
        parser.error(f"'{name}' already exists")

    files = templates.render(project=name, pkg=pkg, manager=manager)
    for rel, content in files.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    print(templates.next_steps(name, pkg, manager))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
