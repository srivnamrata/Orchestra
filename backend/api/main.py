"""
Entry point for uvicorn.
All application logic lives in app.py and the routers/ package.
"""

from backend.api.app import app  # noqa: F401 — re-exported for `uvicorn backend.api.main:app`

if __name__ == "__main__":
    import uvicorn
    from backend.config import get_config

    cfg = get_config()
    uvicorn.run(
        "backend.api.main:app",
        host=cfg.API_HOST,
        port=cfg.API_PORT,
        reload=False,
        log_level=cfg.LOG_LEVEL.lower(),
    )
