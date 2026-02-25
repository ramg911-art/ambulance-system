"""API dependencies - DB session and auth."""
from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.models import Driver

security = HTTPBearer(auto_error=False)


def get_db_session() -> Generator[Session, None, None]:
    """Database session dependency."""
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db_session)]


def get_current_driver(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> Driver:
    """Extract and validate JWT, return current driver."""
    token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if not payload or payload.get("type") != "driver":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    driver_id = payload.get("sub")
    if not driver_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    driver = db.query(Driver).filter(Driver.id == int(driver_id)).first()
    if not driver or not driver.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Driver not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return driver
