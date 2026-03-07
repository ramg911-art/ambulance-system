"""Organization schemas."""
from typing import Optional

from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    """Create organization."""

    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    active: bool = True


class OrganizationUpdate(BaseModel):
    """Update organization."""

    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    active: Optional[bool] = None


class OrganizationResponse(BaseModel):
    """Organization response."""

    id: int
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True
