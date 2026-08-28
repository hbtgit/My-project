from fastapi import FastAPI

from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.modules import INSTALLED_MODULES


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    register_error_handlers(app)

    for module in INSTALLED_MODULES:
        app.include_router(module.router, prefix=settings.api_prefix)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, object]:
        return {"status": "ok", "modules": [m.name for m in INSTALLED_MODULES]}

    return app


app = create_app()
