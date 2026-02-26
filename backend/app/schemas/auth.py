"""Authentication schemas."""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Driver login request."""

    phone: str
    password: str


class AdminLoginRequest(BaseModel):
    """Admin login request."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class DriverLoginResponse(TokenResponse):
    """Driver login response - includes driver info."""

    driver: dict | None = None
