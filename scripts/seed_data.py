from faker import Faker
import sys
import os
import random
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import User, Student, School, ParentStudentLink, UserRole, SurveyResponse, AlertLevel

fake = Faker('es_ES')

def seed_data():
    db = SessionLocal()
    
    print("Fetching schools...")
    # Get schools with coordinates to make map interesting
    # Skip the first 35 to avoid re-seeding the same ones heavily
    schools = db.query(School).filter(School.latitude.isnot(None)).offset(35).limit(50).all()
    
    if not schools:
        print("No more schools found with coordinates.")
        return

    # Pre-calculate password hash for speed
    default_password = generate_password_hash("1234")

    # ... (rest of logic) ...
    # I'll rewrite the loop to be more controlled for colors
    
    for i, school in enumerate(schools):
        print(f"Populating School {i+1}/{len(schools)}: {school.name}")
        
        # Decide School 'Destiny' (Color)
        # 0: Green (Safe), 1: Orange (Warning), 2: Red (Critical)
        destiny = random.choice(['green', 'green', 'orange', 'red']) 
        
        num_teachers = random.randint(3, 8) 
        
        for _ in range(num_teachers):
            teacher_name = fake.name()
            teacher_email = f"{teacher_name.replace(' ', '.').lower()}.{random.randint(1000,9999)}@edu.gva.es"
            
            if db.query(User).filter(User.email == teacher_email).first():
                continue

            teacher = User(
                email=teacher_email,
                hashed_password=default_password,
                full_name=teacher_name,
                role=UserRole.TEACHER,
                teacher_code=fake.bothify(text='??-####').upper(),
                school_id=school.id
            )
            db.add(teacher)
            db.flush() 
            
            classroom = f"{random.choice(['1', '2', '3', '4', '5', '6'])}{random.choice(['A', 'B', 'C'])}"
            
            # Students per class
            num_students = random.randint(15, 25)
            
            # Calculate how many 'bad' surveys we need for the destiny
            bad_surveys_needed = 0
            if destiny == 'red':
                # Force at least one class to be > 20%
                # Let's say this class is the one
                if random.random() < 0.3: # 30% chance this class is the 'bad' one
                    bad_surveys_needed = int(num_students * 0.25) # 25% > 20% -> RED
            elif destiny == 'orange':
                # Force > 5% but < 20%
                # 10% risk
                if random.random() < 0.5:
                    bad_surveys_needed = int(num_students * 0.10) # 10% -> ORANGE
            
            for s_idx in range(num_students):
                s_name = fake.first_name()
                s_last = fake.last_name()
                # Use 5 digits for less collision chance
                student_code = f"{s_name[0]}{s_last[:3]}{random.randint(10000,99999)}".upper()
                
                student = Student(
                    internal_code=student_code,
                    age=random.randint(6, 12),
                    grade_class=classroom,
                    school_id=school.id,
                    teacher_id=teacher.id
                )
                db.add(student)
                db.flush()
                
                # Create Parent
                parent = User(
                    email=f"{fake.user_name()}{random.randint(100,999)}@example.com",
                    hashed_password=default_password,
                    full_name=fake.name(),
                    role=UserRole.PARENT
                )
                db.add(parent)
                db.flush()
                student.parents.append(parent)
                
                # Survey Generation
                # If we need bad surveys for this class
                risk = AlertLevel.LOW
                score = random.randint(0, 30)
                
                if bad_surveys_needed > 0:
                    # Create a bad survey
                    risk = AlertLevel.HIGH
                    score = random.randint(70, 90)
                    bad_surveys_needed -= 1
                elif random.random() < 0.05: # Random noise (5% chance of high risk anyway)
                     risk = AlertLevel.HIGH
                     score = random.randint(60, 80)

                survey = SurveyResponse(
                    student_id=student.id,
                    submitted_by_id=parent.id,
                    raw_answers="{}",
                    calculated_risk_score=score,
                    risk_level=risk,
                    ai_summary="Simulated Risk" if risk != AlertLevel.LOW else "Normal"
                )
                db.add(survey)

        db.commit()

    print("Done! Seeding completed.")
    db.close()

if __name__ == "__main__":
    seed_data()
