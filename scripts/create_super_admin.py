import sys
import os
from sqlalchemy.orm import Session

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import User, UserRole
from app.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        email = "maria@conselleria.es"
        # Check if exists
        curr = db.query(User).filter(User.email == email).first()
        if curr:
            print(f"User {email} already exists.")
            return

        print("Creating Super Admin...")
        sa = User(
            email=email,
            full_name="Maria Conselleria",
            hashed_password=get_password_hash("Maria12345@"),
            role=UserRole.SUPER_ADMIN,
        )
        db.add(sa)
        db.commit()
        print(f"Super Admin created: {email}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
