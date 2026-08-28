"""Feature modules. Add a new module here to mount its routes and register its models."""

from app.core.module import Module
from app.modules.catalog import module as catalog

INSTALLED_MODULES: list[Module] = [
    catalog,
]
