"""Add address, phone, email to organizations. Run once if upgrading from older schema."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.db.session import engine


def migrate():
    cols = [("address", "VARCHAR(500)"), ("phone", "VARCHAR(50)"), ("email", "VARCHAR(255)")]
    with engine.connect() as conn:
        for col_name, col_type in cols:
            try:
                conn.execute(text(f"ALTER TABLE organizations ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"Added column organizations.{col_name}")
            except Exception as e:
                msg = str(e).lower()
                if "already exists" in msg or "duplicate column" in msg:
                    print(f"Column organizations.{col_name} already exists, skipping.")
                else:
                    raise
    print("Migration complete.")


if __name__ == "__main__":
    migrate()
