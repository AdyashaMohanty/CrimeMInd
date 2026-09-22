from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.db.pool import pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open(wait=True)
    yield
    pool.close()


settings = get_settings()
app = FastAPI(
    title="CrimeMind Investigative Intelligence API",
    version="1.0.0",
    description="Case-independent, evidence-backed API for the CrimeMind investigation platform.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {"name": settings.app_name, "version": "1.0.0", "docs": "/docs", "health": f"{settings.api_prefix}/health"}
