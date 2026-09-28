"""FastAPI entrypoint: app factory, lifespan (DB pool), CORS, routers.

Run locally:  uvicorn app.main:app --reload   (from backend/)
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db import create_pool
from app.routers import auth, digest, tasks, topics


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    pool = create_pool(settings)
    # wait=False: the app still boots if the DB is briefly unreachable (e.g. Neon
    # waking from suspend); the pool keeps retrying in the background.
    pool.open(wait=False)
    app.state.pool = pool
    try:
        yield
    finally:
        pool.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Ekko API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(NotImplementedError)
    async def not_implemented_handler(_: Request, exc: NotImplementedError) -> JSONResponse:
        # Stubbed endpoints raise NotImplementedError; surface that as 501 instead of 500.
        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content={"detail": str(exc) or "Not implemented yet"},
        )

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(topics.router)
    app.include_router(digest.router)
    app.include_router(tasks.router)

    return app


app = create_app()
