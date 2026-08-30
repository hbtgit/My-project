# Architecture

## Modular monolith

The IMS is one deployable FastAPI service split into feature modules. Each module owns
its tables, validation, business rules and routes, and talks to other modules only
through their service classes. This keeps the codebase easy to deploy (one container,
one database) while letting modules be built and tested independently (NFR-07).

```
HTTP request -> router -> service -> repository -> SQLAlchemy session -> PostgreSQL
                            |
                            +-> raises DomainError -> JSON error response
```

## Layer rules

| Layer | File | Responsibility | Must not |
|---|---|---|---|
| Router | `router.py` | Parse HTTP input, call one service method, return a schema | Contain business rules or queries |
| Schemas | `schemas.py` | Input validation and normalisation, response shapes | Touch the database |
| Service | `service.py` | Business rules, transactions (`commit`/`rollback`) | Know about HTTP |
| Repository | `repository.py` | Queries | Commit, or enforce business rules |
| Models | `models.py` | Tables and database constraints | Import from other layers |

Business rules are enforced twice where it matters: once in the service for a clear
error message, and once as a database constraint so concurrent requests cannot bypass it
(NFR-10). Services translate `IntegrityError` into `ConflictError`.

## Conventions

- Money: `NUMERIC(12,2)` and `Decimal`, never floats (SRS 7.2). JSON returns money as strings.
- Records with history are deactivated, never deleted (FR-02, business rule 7).
- Every schema change is an Alembic revision. CI runs `alembic check` to catch drift.
- Errors use one shape: `{"error": {"code", "message", "details"}}`.
- Tests mirror the module tree and name SRS acceptance tests where they apply (`test_at01_...`).

## Roadmap

Ordered to follow the proposal's timeline and MVP checklist.

| # | Module | SRS | Notes |
|---|---|---|---|
| 1 | **catalog** (done) | FR-02 | Products, categories |
| 2 | auth | FR-01, FR-08 | Users, roles, password hashing, token or session auth, permission dependency applied to every router, audit log |
| 3 | inventory | FR-04 | Warehouses, `inventory_balances`, append-only `stock_movements`, adjustments with reasons, transfers; row locking or conditional updates to prevent negative stock (AT-02, AT-05) |
| 4 | purchasing | FR-03 | Suppliers, purchase orders with status workflow, goods receipts that post stock movements on confirmation |
| 5 | sales | FR-05 | Sales, receipt numbers, atomic stock deduction, returns and cancellations as compensating movements (AT-03, AT-04) |
| 6 | alerts and reports | FR-06, FR-07 | Low-stock alerts (AT-07), dashboard figures, CSV export (AT-08) |

Decisions to settle with stakeholders before module 3: whether negative stock is ever
allowed, and the costing method for valuation (weighted average or FIFO, business rule 10).
