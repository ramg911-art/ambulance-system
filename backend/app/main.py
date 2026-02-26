"""Ambulance Fleet Management - FastAPI application."""
import logging
import time
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

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

# Trust Cloudflare proxy headers
app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts="*"
)

# Restrict allowed hosts for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "ambu.cfvision.in",
        "driver.cfvision.in",
        "ambuadmin.cfvision.in",
        "localhost",
        "127.0.0.1"
    ]
)

# Enable CORS for all cfvision.in subdomains and localhost dev
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.cfvision\.in|http://localhost(:\d+)?|http://127\.0\.0\.1(:\d+)?",
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
