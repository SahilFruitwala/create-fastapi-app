# create-fastapi-app

Scaffold a production-ready **FastAPI + SQLAlchemy 2.0 (async)** backend with one
command. Optionally wire up **Alembic** migrations and pick your **database** and
**package manager** — all interactively or via flags.

## Quickstart (no install)

```bash
uvx create-fastapi-app myproject
# or
pipx run create-fastapi-app myproject
```

Run with no arguments and you'll be prompted for everything:

```bash
uvx create-fastapi-app
```

You'll be asked for:

- whether to scaffold into the **current directory**
- the **project name**
- the **code/package directory** name (default: `app`)
- the **package manager** — uv / pdm / pip
- the **database** — PostgreSQL (asyncpg) or SQLite (aiosqlite)
- whether to include **Alembic** migrations

## Install

```bash
uv tool install create-fastapi-app   # or: pipx install create-fastapi-app
create-fastapi-app myproject
```

## Usage

```
create-fastapi-app [name] [options]
```

| Argument / flag | Description | Default |
| --- | --- | --- |
| `name` | Project directory name. Use `.` to scaffold into the current directory. | prompted (`myapp`) |
| `-p`, `--package-manager` | Dependency manager: `uv`, `pdm`, or `pip`. | `uv` |
| `-d`, `--package-dir` | Python package / code directory name. | `app` |
| `--db`, `--database` | Database: `postgres` or `sqlite`. | `postgres` |
| `--here` | Scaffold into the current directory instead of a new one. | off |
| `--alembic` / `--no-alembic` | Include or skip Alembic migrations. | included |
| `-y`, `--yes` | Accept all defaults without prompting. | off |

Anything you don't pass as a flag is prompted for interactively. With `--yes`
(or when stdin isn't a TTY), the defaults above are used.

### Examples

```bash
# Fully interactive
uvx create-fastapi-app

# Postgres + Alembic, no prompts
uvx create-fastapi-app myproject -p uv -y

# SQLite, no migrations, into the current directory
uvx create-fastapi-app . --db sqlite --no-alembic -y

# pdm + custom package directory
uvx create-fastapi-app myproject -p pdm -d server
```

## What you get

```
myproject/
├─ app/                     # (your --package-dir)
│  ├─ main.py               # FastAPI app + /health route
│  ├─ core/config.py        # pydantic-settings, reads .env
│  ├─ db/
│  │  ├─ base_class.py      # SQLAlchemy DeclarativeBase
│  │  ├─ base.py            # imports all models (for Alembic)  [alembic only]
│  │  └─ session.py         # async engine + get_db dependency
│  ├─ models/user.py        # example SQLAlchemy model
│  ├─ schemas/user.py       # example Pydantic schemas
│  └─ api/routes/users.py   # example CRUD router
├─ alembic/                 # migration env + versions/         [alembic only]
├─ alembic.ini             #                                    [alembic only]
├─ .env / .env.example      # PROJECT_NAME, DATABASE_URL, API_V1_PREFIX
├─ pyproject.toml
└─ README.md
```

Highlights:

- **Async all the way** — `create_async_engine`, `AsyncSession`, async routes.
  Uses `sqlalchemy[asyncio]` so the required `greenlet` dependency is included.
- **Database-aware** — `DATABASE_URL`, the driver dependency (`asyncpg` vs
  `aiosqlite`), and the docs are set to match your `--db` choice.
- **Alembic done right** — `env.py` reads the URL from your app settings and
  enables **batch mode automatically for SQLite**, so column alterations work
  (SQLite has limited `ALTER TABLE` support). Omit it entirely with
  `--no-alembic`.

## Next steps in a generated project

`cd` into the project (skip if you used `.` / `--here`), then install and run.
The exact commands are printed after scaffolding. For the default uv + Postgres +
Alembic setup:

```bash
cd myproject
uv venv && source .venv/bin/activate && uv pip install -e .

# edit DATABASE_URL in .env (skip for sqlite — it points at a local app.db)
alembic revision --autogenerate -m "initial"
alembic upgrade head

uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs
