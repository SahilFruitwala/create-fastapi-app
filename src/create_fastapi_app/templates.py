"""File templates for the generated project.

Each generated file's body uses the token ``__PKG__`` wherever the chosen
code/package directory name should appear. ``render()`` substitutes it.
"""
from __future__ import annotations

# --- generated project files (keys may also contain __PKG__) ------------------

_FILES: dict[str, str] = {
    "__PKG__/__init__.py": "",
    "__PKG__/core/__init__.py": "",
    "__PKG__/db/__init__.py": "",
    "__PKG__/models/__init__.py": "",
    "__PKG__/schemas/__init__.py": "",
    "__PKG__/api/__init__.py": "",
    "__PKG__/api/routes/__init__.py": "",

    ".env": '''PROJECT_NAME="My API"
DATABASE_URL="__DB_URL__"
API_V1_PREFIX="/api/v1"
''',

    ".env.example": '''PROJECT_NAME="My API"
DATABASE_URL="__DB_URL__"
API_V1_PREFIX="/api/v1"
''',

    ".gitignore": '''# Byte-compiled / optimized / cache
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
build/
dist/
*.egg-info/
.eggs/

# Virtual environments
.venv/
venv/
env/

# Environment / secrets
.env
.env.*
!.env.example

# Databases
*.sqlite3
*.db

# Package managers
.pdm-python
.pdm-build/
__pypackages__/

# Test / coverage
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/

# Linters / type checkers
.ruff_cache/
.mypy_cache/

# Editors / OS
.idea/
.vscode/
.DS_Store
''',

    "pyproject.toml": '''[project]
name = "app"
version = "0.1.0"
description = "FastAPI backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi[standard]>=0.111",
    "sqlalchemy[asyncio]>=2.0",
    "alembic>=1.13",
    "__DB_DRIVER__",
    "pydantic-settings>=2.2",
    "pydantic[email]>=2.7",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["__PKG__*"]
''',

    "__PKG__/core/config.py": '''from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "My API"
    DATABASE_URL: str = "__DB_URL__"
    API_V1_PREFIX: str = "/api/v1"


settings = Settings()
''',

    "__PKG__/db/base_class.py": '''from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
''',

    "__PKG__/db/session.py": '''from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from __PKG__.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
''',

    "__PKG__/models/user.py": '''from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from __PKG__.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
''',

    "__PKG__/schemas/user.py": '''from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
''',

    "__PKG__/api/routes/users.py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from __PKG__.db.session import get_db
from __PKG__.models.user import User
from __PKG__.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    user = User(**payload.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
''',

    "__PKG__/main.py": '''from fastapi import FastAPI

from __PKG__.api.routes import users
from __PKG__.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(users.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}
''',

}

# --- alembic-specific files (only generated when alembic is enabled) ----------

_ALEMBIC_FILES: dict[str, str] = {
    "alembic/versions/.gitkeep": "",

    "__PKG__/db/base.py": '''# Import Base and ALL models here so Alembic autogenerate sees every table.
from __PKG__.db.base_class import Base  # noqa: F401
from __PKG__.models.user import User  # noqa: F401
''',

    "alembic.ini": '''[alembic]
script_location = alembic
prepend_sys_path = .
# sqlalchemy.url is set in alembic/env.py from app settings.

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
''',

    "alembic/env.py": '''import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from __PKG__.core.config import settings
from __PKG__.db.base import Base  # noqa: F401  (imports all models)

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite can't ALTER most things; batch mode emits copy-and-move DDL.
        render_as_batch=url.startswith("sqlite"),
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # SQLite can't ALTER most things; batch mode emits copy-and-move DDL.
        render_as_batch=connection.dialect.name == "sqlite",
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
''',

    "alembic/script.py.mako": '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
''',
}

# --- supported databases -----------------------------------------------------

_DATABASES: dict[str, dict[str, str]] = {
    "postgres": {
        "url": "postgresql+asyncpg://postgres:postgres@localhost:5432/app",
        "driver": "asyncpg>=0.29",
        "label": "PostgreSQL (asyncpg)",
    },
    "sqlite": {
        "url": "sqlite+aiosqlite:///./app.db",
        "driver": "aiosqlite>=0.19",
        "label": "SQLite (aiosqlite)",
    },
}

# --- per-manager setup blocks for the README ---------------------------------

_SETUP = {
    "uv": '''```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```''',
    "pdm": '''```bash
pdm install
```
Run commands below with a `pdm run` prefix (or `eval $(pdm venv activate)`).''',
    "pip": '''```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```''',
}


def _readme(project: str, pkg: str, manager: str, alembic: bool, db: str) -> str:
    prefix = "pdm run " if manager == "pdm" else ""
    stack = f"FastAPI + SQLAlchemy 2.0 (async, {_DATABASES[db]['label']})"
    if alembic:
        stack += " + Alembic"
    migrations = ""
    if alembic:
        migrations = f'''## Database migrations

```bash
{prefix}alembic revision --autogenerate -m "initial"
{prefix}alembic upgrade head
```

'''
    return f'''# {project}

{stack}. Code lives in `{pkg}/`.

## Setup ({manager})

{_SETUP[manager]}

{migrations}## Run

```bash
{prefix}uvicorn {pkg}.main:app --reload
```

Open http://127.0.0.1:8000/docs
'''


def render(
    project: str, pkg: str, manager: str, alembic: bool = True, db: str = "postgres"
) -> dict[str, str]:
    """Return {relative_path: file_content} for the new project."""
    dbcfg = _DATABASES[db]
    out: dict[str, str] = {}
    files = dict(_FILES)
    if alembic:
        files.update(_ALEMBIC_FILES)
    for path, body in files.items():
        if not alembic and path == "pyproject.toml":
            body = body.replace('    "alembic>=1.13",\n', "")
        body = body.replace("__DB_URL__", dbcfg["url"]).replace(
            "__DB_DRIVER__", dbcfg["driver"]
        )
        out[path.replace("__PKG__", pkg)] = body.replace("__PKG__", pkg)
    out["README.md"] = _readme(project, pkg, manager, alembic, db)
    return out


def next_steps(
    project: str, pkg: str, manager: str, alembic: bool = True, db: str = "postgres"
) -> str:
    prefix = "pdm run " if manager == "pdm" else ""
    if manager == "uv":
        install = "uv venv && source .venv/bin/activate && uv pip install -e ."
    elif manager == "pdm":
        install = "pdm install"
    else:
        install = "python -m venv .venv && source .venv/bin/activate && pip install -e ."
    location = "the current directory" if project == "." else f"'{project}/'"
    cd_line = "" if project == "." else f"  cd {project}\n"
    migrate_lines = ""
    if alembic:
        migrate_lines = (
            f"  {prefix}alembic revision --autogenerate -m 'initial'\n"
            f"  {prefix}alembic upgrade head\n"
        )
    db_hint = (
        "  # edit DATABASE_URL in .env, then:\n"
        if db != "sqlite"
        else "  # DATABASE_URL in .env points at a local app.db file\n"
    )
    return (
        f"\nDone. Scaffolded {location} (package: {pkg}, manager: {manager}, "
        f"db: {db}, alembic: {'yes' if alembic else 'no'}).\n\n"
        f"Next:\n"
        f"{cd_line}"
        f"  {install}\n"
        f"{db_hint}"
        f"{migrate_lines}"
        f"  {prefix}uvicorn {pkg}.main:app --reload\n"
    )
