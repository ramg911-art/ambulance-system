"""Ambulance Fleet Management - FastAPI application."""
import logging
import time
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    trips,
    gps,
    vehicles,
    preset_locations,
    preset_destinations,
    billing,
    drivers,
    tariffs,
    organizations,
)
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: ensure DB tables exist. Shutdown: cleanup."""
    init_db()
    yield


app = FastAPI(
    title="Ambulance Fleet Backend",
    description="GPS tracking, preset tariff billing, distance tariff billing",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request to help debug save failures."""
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logging.info(
        "%s %s -> %s (%.0fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response

app.include_router(auth.router)
app.include_router(trips.router)
app.include_router(gps.router)
app.include_router(vehicles.router)
app.include_router(preset_locations.router)
app.include_router(preset_destinations.router)
app.include_router(billing.router)
app.include_router(drivers.router)
app.include_router(tariffs.router)
app.include_router(organizations.router)


@app.get("/health")
def health() -> dict:
    """Health check for load balancers."""
    return {"status": "ok"}
