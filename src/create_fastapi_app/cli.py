"""create-fastapi-app — scaffold a FastAPI + SQLAlchemy + Alembic backend."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import templates

MANAGERS = ["uv", "pdm", "pip"]
DATABASES = ["postgres", "sqlite"]


def _prompt(text: str, default: str) -> str:
    try:
        value = input(f"{text} [{default}]: ").strip()
    except EOFError:
        return default
    return value or default


def _prompt_yes_no(text: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        try:
            value = input(f"{text} [{suffix}]: ").strip().lower()
        except EOFError:
            return default
        if not value:
            return default
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print("Please answer y or n.")


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


def _prompt_database() -> str:
    print("Database:")
    print("  1) postgres  (asyncpg, recommended)")
    print("  2) sqlite    (aiosqlite, zero-setup local file)")
    while True:
        try:
            choice = input("Choose [1]: ").strip() or "1"
        except EOFError:
            return "postgres"
        mapping = {"1": "postgres", "2": "sqlite",
                   "postgres": "postgres", "sqlite": "sqlite"}
        if choice in mapping:
            return mapping[choice]
        print("Please enter 1 or 2.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="create-fastapi-app",
        description="Scaffold a FastAPI + SQLAlchemy (async) + Alembic backend.",
    )
    parser.add_argument("name", nargs="?", help="project directory name ('.' for current dir)")
    parser.add_argument(
        "-p", "--package-manager", choices=MANAGERS,
        help="dependency manager to target (uv, pdm, or pip)",
    )
    parser.add_argument(
        "-d", "--package-dir",
        help="name of the Python package / code directory (default: app)",
    )
    parser.add_argument(
        "--db", "--database", dest="db", choices=DATABASES,
        help="database to target (postgres or sqlite)",
    )
    parser.add_argument(
        "--here", action="store_true",
        help="scaffold into the current directory instead of a new one",
    )
    alembic_group = parser.add_mutually_exclusive_group()
    alembic_group.add_argument(
        "--alembic", dest="alembic", action="store_true", default=None,
        help="include Alembic migrations (default)",
    )
    alembic_group.add_argument(
        "--no-alembic", dest="alembic", action="store_false",
        help="skip Alembic migrations",
    )
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="accept defaults without prompting",
    )
    args = parser.parse_args(argv)

    interactive = sys.stdin.isatty() and not args.yes

    if args.here:
        name = "."
    elif args.name:
        name = args.name
    elif interactive:
        if _prompt_yes_no("Scaffold into the current directory?", default=False):
            name = "."
        else:
            name = _prompt("Project name", "myapp")
    else:
        name = "myapp"

    pkg = args.package_dir or (
        _prompt("Main code/package directory", "app") if interactive else "app"
    )
    if not pkg.isidentifier():
        parser.error(f"package dir '{pkg}' is not a valid Python identifier")

    manager = args.package_manager or (
        _prompt_manager() if interactive else "uv"
    )

    db = args.db or (_prompt_database() if interactive else "postgres")

    if args.alembic is not None:
        alembic = args.alembic
    elif interactive:
        alembic = _prompt_yes_no("Include Alembic migrations?", default=True)
    else:
        alembic = True

    target = Path(name)
    if name == ".":
        if any(target.iterdir()):
            if not (interactive and _prompt_yes_no(
                "Current directory is not empty. Continue?", default=False
            )):
                parser.error("current directory is not empty")
    elif target.exists():
        parser.error(f"'{name}' already exists")

    files = templates.render(
        project=name, pkg=pkg, manager=manager, alembic=alembic, db=db
    )
    for rel, content in files.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    print(templates.next_steps(name, pkg, manager, alembic, db))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
