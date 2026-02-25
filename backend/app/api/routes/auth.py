"""Authentication routes - driver and admin login."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.core.security import create_access_token, verify_password
from app.models import AdminUser, Driver
from app.schemas.auth import AdminLoginRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def driver_login(data: LoginRequest, db: DbSession) -> TokenResponse:
    """Driver login using phone and password. Returns JWT."""
    driver = db.query(Driver).filter(Driver.phone == data.phone).first()
    if not driver or not driver.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
        )
    if not verify_password(data.password, driver.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
        )
    token = create_access_token({"sub": str(driver.id), "type": "driver"})
    return TokenResponse(access_token=token)


@router.post("/admin-login", response_model=TokenResponse)
def admin_login(data: AdminLoginRequest, db: DbSession) -> TokenResponse:
    """Admin login using username and password. Returns JWT."""
    admin = db.query(AdminUser).filter(AdminUser.username == data.username).first()
    if not admin or not admin.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not verify_password(data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token({"sub": admin.username, "type": "admin"})
    return TokenResponse(access_token=token)
