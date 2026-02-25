"""GPS service - live tracking via Redis and GPS log storage."""
import json
from datetime import datetime
from typing import Optional

import redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import GPSLog, Vehicle


class GPSService:
    """Service for GPS tracking and logging."""

    LIVE_KEY_PREFIX = "vehicle:live:"
    LIVE_TTL = 300  # 5 minutes

    def __init__(self, db: Session):
        self.db = db
        self._redis: Optional[redis.Redis] = None

    @property
    def redis_client(self) -> redis.Redis:
        """Lazy Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(settings.redis_url)
        return self._redis

    def update_vehicle_location(
        self,
        vehicle_id: int,
        latitude: float,
        longitude: float,
        trip_id: Optional[int] = None,
    ) -> None:
        """Update live vehicle location in Redis and optionally store GPS log."""
        key = f"{self.LIVE_KEY_PREFIX}{vehicle_id}"
        data = {
            "vehicle_id": vehicle_id,
            "latitude": latitude,
            "longitude": longitude,
            "trip_id": trip_id,
            "last_updated": datetime.utcnow().isoformat(),
        }
        self.redis_client.setex(
            key,
            self.LIVE_TTL,
            json.dumps(data),
        )

    def store_gps_log(
        self,
        vehicle_id: int,
        latitude: float,
        longitude: float,
        trip_id: Optional[int] = None,
    ) -> GPSLog:
        """Store GPS log in database."""
        log = GPSLog(
            vehicle_id=vehicle_id,
            trip_id=trip_id,
            latitude=latitude,
            longitude=longitude,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_live_vehicle_locations(self) -> list[dict]:
        """Get all live vehicle locations from Redis."""
        keys = self.redis_client.keys(f"{self.LIVE_KEY_PREFIX}*")
        result = []
        for key in keys:
            data = self.redis_client.get(key)
            if data:
                result.append(json.loads(data))
        return result
