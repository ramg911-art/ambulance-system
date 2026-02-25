"""Ambulance Fleet Management - FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
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
