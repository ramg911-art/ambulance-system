"""Application configuration."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment."""

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ambulance:ambulance_secret@localhost:5432/ambulance_fleet",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    secret_key: str = os.getenv("SECRET_KEY", "change_this_to_long_random_string")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    distance_tariff_per_km: float = float(os.getenv("DISTANCE_TARIFF_PER_KM", "50.0"))


settings = Settings()
