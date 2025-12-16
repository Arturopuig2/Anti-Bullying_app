
import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import School

def get_codes():
    db = SessionLocal()
    try:
        schools = db.query(School).all()
        print(f"Check: found {len(schools)} schools.")
        for s in schools:
            print(f"School: {s.name} | Code: {s.center_code}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    get_codes()
