from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import routes_schools, routes_scores, routes_subscribers
from app.config import get_settings
from app.db.session import init_db
from app.distribution_wiring import register_distribution_hooks
from app.jobs.scheduler import start_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    register_distribution_hooks()
    app.state.scheduler = start_scheduler()
    yield
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

bulletin_dir = Path(settings.bulletin_storage_dir)
bulletin_dir.mkdir(parents=True, exist_ok=True)
app.mount("/bulletins", StaticFiles(directory=str(bulletin_dir)), name="bulletins")


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Liveness check used by the hosting platform and uptime monitoring."""
    return {"status": "ok"}
