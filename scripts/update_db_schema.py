from sqlalchemy import create_engine, text
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SQLALCHEMY_DATABASE_URL

def update_schema():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        print("Checking partial schema updates...")
        
        # Helper to add column if not exists (SQLite doesn't support IF NOT EXISTS in ALTER TABLE well in all versions, so we try/except)
        statements = [
            "ALTER TABLE schools ADD COLUMN center_code VARCHAR",
            "ALTER TABLE schools ADD COLUMN latitude FLOAT",
            "ALTER TABLE schools ADD COLUMN longitude FLOAT",
            "ALTER TABLE schools ADD COLUMN phone VARCHAR"
        ]
        
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                print(f"Executed: {stmt}")
            except Exception as e:
                # If column exists, it throws error. We ignore it.
                if "duplicate column name" in str(e).lower():
                    print(f"Skipped (already exists): {stmt}")
                else:
                    print(f"Error executing {stmt}: {e}")

        conn.commit()
        print("Schema update finished.")

if __name__ == "__main__":
    update_schema()
