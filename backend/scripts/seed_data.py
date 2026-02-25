"""Seed initial data for development."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.models import (
    AdminUser,
    Organization,
    Driver,
    Vehicle,
    PresetLocation,
    PresetDestination,
    FixedTariff,
)


def seed():
    init_db()
    db = SessionLocal()
    try:
        # Always ensure admin user exists
        if not db.query(AdminUser).first():
            admin = AdminUser(
                username="admin",
                password_hash=hash_password("admin123"),
                active=True,
            )
            db.add(admin)
            db.commit()
            print("Admin user created. Login: admin / admin123")

        if db.query(Organization).first():
            print("Org data already exists, skipping org/driver/vehicle seed.")
            return

        org = Organization(name="City Ambulance Service", code="CAS", active=True)
        db.add(org)
        db.flush()

        driver = Driver(
            organization_id=org.id,
            name="John Driver",
            phone="+1234567890",
            password_hash=hash_password("driver123"),
            license_number="DL-001",
            active=True,
        )
        db.add(driver)

        vehicle = Vehicle(
            organization_id=org.id,
            registration_number="AMB-001",
            make_model="Mercedes Sprinter",
            active=True,
        )
        db.add(vehicle)
        db.flush()

        loc = PresetLocation(
            organization_id=org.id,
            name="City Hospital",
            latitude=12.9716,
            longitude=77.5946,
            radius_meters=200,
            active=True,
        )
        db.add(loc)
        db.flush()

        dest = PresetDestination(
            name="Central Station",
            latitude=12.9784,
            longitude=77.6408,
        )
        db.add(dest)
        db.flush()

        tariff = FixedTariff(
            organization_id=org.id,
            source_id=loc.id,
            destination_id=dest.id,
            amount=500.0,
        )
        db.add(tariff)

        db.commit()
        print("Seed completed. Driver: +1234567890 / driver123 | Admin: admin / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
