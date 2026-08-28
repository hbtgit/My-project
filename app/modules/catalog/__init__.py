"""Catalog module: products and categories (SRS FR-02)."""

from app.core.module import Module
from app.modules.catalog import models  # noqa: F401  (registers tables on Base.metadata)
from app.modules.catalog.router import router

module = Module(
    name="catalog",
    router=router,
    description="Products and categories with unique SKUs, pricing and reorder levels.",
)
