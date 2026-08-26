from dataclasses import dataclass

from fastapi import APIRouter


@dataclass(frozen=True)
class Module:
    """A self-contained feature area (catalog, inventory, purchasing, ...).

    Each module owns its models, schemas, service logic and router. The app
    mounts every module listed in app.modules.INSTALLED_MODULES.
    """

    name: str
    router: APIRouter
    description: str = ""
