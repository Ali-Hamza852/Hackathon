import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_bulletins, routes_schools, routes_scores, routes_subscribers
from app.config import get_settings
from app.db.session import init_db
from app.distribution_wiring import register_distribution_hooks
from app.jobs.scheduler import start_scheduler

settings = get_settings()

RUNNING_ON_VERCEL = bool(os.environ.get("VERCEL"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    register_distribution_hooks()
    if not RUNNING_ON_VERCEL:
        app.state.scheduler = start_scheduler()
    yield
    if not RUNNING_ON_VERCEL:
        app.state.scheduler.shutdown(wait=False)


app = FastAPI(
    title="SAANS API",
    description="Smog Advisory & School Closure decision-support API for Lahore schools.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_base_url, "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_schools.router)
app.include_router(routes_scores.router)
app.include_router(routes_subscribers.router)
app.include_router(routes_bulletins.router)

try:
    from distribution.whatsapp.bot import router as whatsapp_router

    app.include_router(whatsapp_router)
except ImportError:
    pass


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Liveness check used by the hosting platform and uptime monitoring."""
    return {"status": "ok"}
