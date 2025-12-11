from app.database import SessionLocal
from app.models import User, UserRole, School
from app.security import get_password_hash

def seed_db():
    db = SessionLocal()
    
    # Crear Colegio
    if not db.query(School).first():
        school = School(name="Colegio Demo", address="Madrid", contact_email="demo@school.com")
        db.add(school)
        db.commit()
    
    # Crear Usuario Admin
    email = "admin@example.com"
    if not db.query(User).filter(User.email == email).first():
        pwd = get_password_hash("secreto123")
        user = User(
            email=email,
            hashed_password=pwd,
            full_name="Admin Principal",
            role=UserRole.SCHOOL_ADMIN,
        )
        db.add(user)
        db.commit()
        print(f"Usuario creado: {email} / secreto123")
    else:
        print("Usuario ya existe")
        
    db.close()

if __name__ == "__main__":
    seed_db()
