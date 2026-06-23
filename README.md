# create-fastapi-app

Scaffold a FastAPI + SQLAlchemy 2.0 (async) + Alembic backend with one command.

## Use it (no install)

```bash
uvx create-fastapi-app myproject
# or
pipx run create-fastapi-app myproject
```

You'll be prompted for the package manager (uv / pdm / pip) and the code
directory name. Or pass them as flags:

```bash
uvx create-fastapi-app myproject --package-manager pdm --package-dir server
uvx create-fastapi-app myproject -p uv -d app --yes
```

## Install it

```bash
uv tool install create-fastapi-app   # or: pipx install create-fastapi-app
create-fastapi-app myproject
```
