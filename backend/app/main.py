"""Ambulance Fleet Management - FastAPI application."""
import logging
import time
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from fastapi import FastAPI, Request

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

# CORS: Cloudflare Tunnel may not forward preflight; handle OPTIONS explicitly
CORS_ORIGINS = [
    "https://driver.cfvision.in",
    "https://ambuadmin.cfvision.in",
    "https://ambu.cfvision.in",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5176",
]


@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    """CORS: handle preflight OPTIONS and add headers to all responses."""
    from starlette.responses import Response

    origin = request.headers.get("origin", "")
    allowed = origin in CORS_ORIGINS or (origin and ".cfvision.in" in origin)
    allow_origin = origin if allowed else CORS_ORIGINS[0] if CORS_ORIGINS else "*"

    cors_headers = {
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Credentials": "true",
    }

    if request.method == "OPTIONS":
        return Response(status_code=200, headers={**cors_headers, "Access-Control-Max-Age": "86400"})

    response = await call_next(request)
    for k, v in cors_headers.items():
        response.headers[k] = v
    return response


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
