"""Authentication schemas."""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Driver login request."""

    phone: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
