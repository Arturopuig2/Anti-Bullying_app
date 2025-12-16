
import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import User, Student, UserRole, ParentStudentLink, School
from app.security import get_password_hash
import uuid

def create_demo_chain():
    db = SessionLocal()
    try:
        # 1. Find an active school with students
        school = db.query(School).join(Student).first()
        if not school:
            print("No active school found.")
            return

        print(f"Selected School: {school.name} (Code: {school.center_code})")

        # 2. Get/Create School Admin (Director)
        director_email = f"director_{school.center_code}@demo.com".lower()
        director = db.query(User).filter(User.email == director_email).first()
        if not director:
            director = User(
                email=director_email,
                full_name="Director Demo",
                hashed_password=get_password_hash("123456"),
                role=UserRole.SCHOOL_ADMIN,
                school_id=school.id
            )
            db.add(director)
            db.commit()
            db.refresh(director)
        else:
            # Ensure pwd is known
            director.hashed_password = get_password_hash("123456")
            db.commit()

        # 3. Get Teacher
        # Find a student first to get their teacher
        student = db.query(Student).filter(Student.school_id == school.id).first()
        if not student:
            print("No student found.")
            return

        teacher = db.query(User).filter(User.id == student.teacher_id).first()
        if not teacher:
            print("Student has no teacher?")
            return
        
        # Reset teacher pwd to be sure
        teacher.hashed_password = get_password_hash("123456")
        db.commit()

        # 4. Create Parent
        parent_email = "padre_demo@demo.com"
        parent = db.query(User).filter(User.email == parent_email).first()
        if not parent:
            parent = User(
                email=parent_email,
                full_name="Padre Demo",
                hashed_password=get_password_hash("123456"),
                role=UserRole.PARENT
            )
            db.add(parent)
            db.commit()
            db.refresh(parent)
        else:
            parent.hashed_password = get_password_hash("123456")
            db.commit()

        # 5. Link Parent to Student
        link = db.query(ParentStudentLink).filter_by(parent_id=parent.id, student_id=student.id).first()
        if not link:
            link = ParentStudentLink(parent_id=parent.id, student_id=student.id)
            db.add(link)
            db.commit()

        print("\n=== CREDENTIALS ===")
        print(f"School: {school.name}")
        print(f"Student: {student.internal_code}")
        print("-" * 20)
        print(f"DIRECTOR: {director_email} / 123456")
        print(f"PROFESOR: {teacher.email} / 123456")
        print(f"PADRE:    {parent_email} / 123456")
        print("===================")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_chain()
