# Inventory Management System (IMS) - Backend

Modular FastAPI backend for the Inventory Management System described in the project
proposal and SRS. This repository is the foundation plus the **first module, Catalog**
(products and categories, SRS FR-02).

Stack, as recommended in the proposal: Python, FastAPI, SQLAlchemy 2, PostgreSQL,
Alembic migrations, Pytest, Docker.

## What is included

**Core foundation (`app/core`)**, shared by every module:

- Settings from environment variables (`IMS_*`), see `.env.example`
- Database engine, per-request session, and a declarative `Base` with stable constraint names
- Domain error types (`NotFoundError`, `ConflictError`, `ValidationFailedError`) mapped to
  consistent JSON error responses
- Pagination helpers and a `Module` contract used to plug feature modules into the app

**Catalog module (`app/modules/catalog`)**

| Requirement | How it is covered |
|---|---|
| FR-02 create, view, edit, search, deactivate products | REST endpoints below |
| FR-02 / Business rule 1 unique SKU (AT-01) | Service check plus a database unique constraint; SKUs are normalised to upper case so `abc-1` and `ABC-1` collide |
| FR-02 product fields | SKU, barcode, name, description, category, unit of measure, cost price, selling price, reorder level |
| FR-02 retain history on deactivation | Products are deactivated, never deleted; the SKU stays reserved |
| Data integrity notes (SRS 7.2) | Money stored as `NUMERIC(12,2)`, check constraints for non-negative prices and reorder levels |

Endpoints (interactive docs at `/docs` once running):

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness and installed modules |
| GET, POST | `/api/categories` | List (filter `is_active`) / create |
| GET, PATCH | `/api/categories/{id}` | Read / update (including deactivate via `is_active`) |
| GET | `/api/products` | List with `q` (name, SKU, barcode), `category_id`, `is_active`, `limit`, `offset` |
| POST | `/api/products` | Create |
| GET | `/api/products/{id}` | Read |
| GET | `/api/products/by-sku/{sku}` | Look up by SKU |
| PATCH | `/api/products/{id}` | Partial update (SKU is immutable) |
| POST | `/api/products/{id}/deactivate` and `/activate` | Change status |

Not yet included: authentication and role permissions. Endpoints are currently open; the
auth module is next on the roadmap and will add the permission checks the SRS requires.

## Project layout

```
app/
  main.py                 # create_app(): mounts every installed module
  core/                   # config, database, errors, pagination, module contract
  modules/
    __init__.py           # INSTALLED_MODULES registry
    catalog/
      models.py           # SQLAlchemy tables
      schemas.py          # Pydantic request/response models and validation
      repository.py       # queries
      service.py          # business rules
      router.py           # HTTP layer (thin)
migrations/               # Alembic, one revision per schema change
tests/                    # pytest, mirrors app/modules
docs/architecture.md      # module conventions and roadmap
```

## Getting started

### Option A: Docker (API and PostgreSQL)

```bash
docker compose up --build
# API on http://localhost:8000, docs on http://localhost:8000/docs
```

Migrations run automatically when the API container starts.

### Option B: Local Python

Requires Python 3.11+ and a PostgreSQL database.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env               # set IMS_DATABASE_URL
docker compose up -d db            # or use your own PostgreSQL
alembic upgrade head
uvicorn app.main:app --reload
```

## Tests and checks

```bash
pytest                              # in-memory SQLite, needs nothing installed
IMS_TEST_DATABASE_URL=postgresql+psycopg://ims:ims@localhost:5432/ims_test pytest
ruff check . && ruff format --check .
alembic check                       # fails if models and migrations drift apart
```

Use a disposable database for `IMS_TEST_DATABASE_URL`; the suite drops and recreates
tables. GitHub Actions (`.github/workflows/ci.yml`) runs lint, both test passes and the
migration check on every push and pull request.

## Adding the next module

See [docs/architecture.md](docs/architecture.md). In short: create
`app/modules/<name>/` with the same five files, expose a `module = Module(...)` in its
`__init__.py`, add it to `INSTALLED_MODULES`, then run
`alembic revision --autogenerate -m "<name>"` and review the generated migration.

## Pushing to your GitHub

1. Create an empty repository on GitHub (no README, .gitignore or license, so the first
   push does not conflict). For example `ims-backend`.
2. From this folder:

```bash
git init -b main
git add .
git commit -m "Foundation and catalog module"
git remote add origin https://github.com/<your-username>/ims-backend.git
git push -u origin main
```

If you use SSH, the remote is `git@github.com:<your-username>/ims-backend.git`. After the
push, the CI workflow runs automatically under the repository's Actions tab.
