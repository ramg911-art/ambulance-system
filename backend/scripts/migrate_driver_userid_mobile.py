"""Rename drivers.phone to user_id and add mobile column. Run once if upgrading from older schema."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.db.session import engine


def migrate():
    """Rename phone -> user_id and add mobile. Uses raw SQL for compatibility."""
    with engine.connect() as conn:
        # PostgreSQL: ALTER COLUMN RENAME, ADD COLUMN
        # SQLite: ALTER TABLE RENAME COLUMN (3.25.0+), else recreate
        dialect = engine.dialect.name
        try:
            if dialect == "postgresql":
                conn.execute(text("ALTER TABLE drivers RENAME COLUMN phone TO user_id"))
                conn.commit()
                print("Renamed drivers.phone to drivers.user_id")
            elif dialect == "sqlite":
                conn.execute(text("ALTER TABLE drivers RENAME COLUMN phone TO user_id"))
                conn.commit()
                print("Renamed drivers.phone to drivers.user_id")
            else:
                # Generic fallback - try rename
                conn.execute(text("ALTER TABLE drivers RENAME COLUMN phone TO user_id"))
                conn.commit()
                print("Renamed drivers.phone to drivers.user_id")
        except Exception as e:
            if "does not exist" in str(e).lower() or "no such column" in str(e).lower():
                print("Column phone may already be renamed, skipping.")
            else:
                raise

        # Add mobile column
        try:
            conn.execute(text("ALTER TABLE drivers ADD COLUMN mobile VARCHAR(20)"))
            conn.commit()
            print("Added column drivers.mobile")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("Column drivers.mobile already exists, skipping.")
            else:
                raise

    print("Migration complete.")


if __name__ == "__main__":
    migrate()
