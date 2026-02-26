"""Ambulance Fleet Management - FastAPI application."""
import logging
import re
import time
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
CORS_ORIGIN_REGEX = re.compile(
    r"^https://.*\.cfvision\.in$|^http://localhost(:\d+)?$|^http://127\.0\.0\.1(:\d+)?$"
)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.cfvision\.in|http://localhost(:\d+)?|http://127\.0\.0\.1(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


def _cors_headers_for(request: Request) -> dict:
    """Return CORS headers to echo back the request origin if allowed."""
    origin = request.headers.get("origin")
    if origin and CORS_ORIGIN_REGEX.match(origin):
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    return {}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers are present on error responses (fixes 500 hiding behind CORS error)."""
    if isinstance(exc, HTTPException):
        raise exc  # Let FastAPI handle HTTPException (401, 404, etc.)
    logging.exception("Unhandled exception: %s", exc)
    headers = _cors_headers_for(request)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=headers,
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
    # Ensure CORS headers on all responses (incl. 4xx/5xx) when origin is allowed
    origin = request.headers.get("origin")
    if origin and CORS_ORIGIN_REGEX.match(origin) and "access-control-allow-origin" not in {
        k.lower() for k in response.headers
    }:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
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
