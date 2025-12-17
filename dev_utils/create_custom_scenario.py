
import sys
import os
import random
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import User, Student, UserRole, ParentStudentLink, School
from app.security import get_password_hash

def create_custom_scenario():
    db = SessionLocal()
    try:
        print("Starting Custom Scenario Creation...")
        
        # 1. Use Specific School (46009371)
        target_code = "46009371"
        school = db.query(School).filter(School.center_code == target_code).first()
        if not school:
            print(f"Error: School {target_code} NOT FOUND. Aborting.")
            return
        
        print(f"Using School: {school.name} ({school.center_code})")

        # 2. Director: Joshua (laura@hotmail.com) -> Requested as Laura
        director_email = "laura@hotmail.com"
        director = db.query(User).filter(User.email == director_email).first()
        if not director:
            director = User(
                email=director_email,
                full_name="Laura Director",
                hashed_password=get_password_hash("123456"),
                role=UserRole.SCHOOL_ADMIN,
                school_id=school.id
            )
            db.add(director)
            print(f"Created Director: {director.email}")
        else:
            # Ensure correct association and pwd
            director.school_id = school.id
            director.role = UserRole.SCHOOL_ADMIN
            director.hashed_password = get_password_hash("123456")
            print(f"Updated Director: {director.email}")
        
        db.commit()

        # 3. Teacher: Alvaro (meferal@hotmail.com)
        teacher_email = "meferal@hotmail.com"
        teacher = db.query(User).filter(User.email == teacher_email).first()
        if not teacher:
            teacher = User(
                email=teacher_email,
                full_name="Alvaro Profesor",
                hashed_password=get_password_hash("123456"),
                role=UserRole.TEACHER,
                school_id=school.id,
                teacher_code="PROF-ALVARO"
            )
            db.add(teacher)
            print(f"Created Teacher: {teacher.email}")
        else:
            teacher.school_id = school.id
            teacher.role = UserRole.TEACHER
            teacher.hashed_password = get_password_hash("123456")
            print(f"Updated Teacher: {teacher.email}")
        
        db.commit()
        db.refresh(teacher)

        # 4. Students (25 Total)
        # Check if already has students to avoid duplicates if re-run
        current_count = db.query(Student).filter(Student.teacher_id == teacher.id).count()
        students_needed = 25 - current_count
        
        # Ensure Elvira exists
        elvira = db.query(Student).filter(Student.name == "Elvira", Student.teacher_id == teacher.id).first()
        if not elvira:
            elvira = Student(
                internal_code=f"S-ELVIRA-{random.randint(1000,9999)}",
                name="Elvira",
                age=16,
                grade_class="4º ESO A",
                school_id=school.id,
                teacher_id=teacher.id
            )
            db.add(elvira)
            db.commit()
            print("Created Student: Elvira")
            students_needed -= 1 # We just created one
        else:
            print("Student Elvira already exists")

        # Create remaining random students
        if students_needed > 0:
            print(f"Creating {students_needed} filler students...")
            for i in range(students_needed):
                s = Student(
                    internal_code=f"S-GEN-{random.randint(10000,99999)}",
                    name=f"Alumno {i+1}",
                    age=16,
                    grade_class="4º ESO A",
                    school_id=school.id,
                    teacher_id=teacher.id
                )
                db.add(s)
            db.commit()
        
        db.refresh(elvira) # Ensure we have the ID

        # 4.5 Ensure all teacher's students are in the correct school
        # (Migration fix for when we changed schools)
        teacher_students = db.query(Student).filter(Student.teacher_id == teacher.id).all()
        for s in teacher_students:
            if s.school_id != school.id:
                s.school_id = school.id
                print(f"Migrated Student {s.internal_code} to new school.")
        db.commit()

        # 5. Parent: Arturo (arturo@hotmail.com)
        parent_email = "arturo@hotmail.com"
        parent = db.query(User).filter(User.email == parent_email).first()
        if not parent:
            parent = User(
                email=parent_email,
                full_name="Arturo Padre",
                hashed_password=get_password_hash("123456"),
                role=UserRole.PARENT
            )
            db.add(parent)
            print(f"Created Parent: {parent.email}")
        else:
            parent.hashed_password = get_password_hash("123456")
            print(f"Updated Parent: {parent.email}")
        
        db.commit()
        db.refresh(parent)

        # 6. Link Parent -> Elvira
        link = db.query(ParentStudentLink).filter_by(parent_id=parent.id, student_id=elvira.id).first()
        if not link:
            link = ParentStudentLink(parent_id=parent.id, student_id=elvira.id)
            db.add(link)
            db.commit()
            print("Linked Arturo to Elvira")
        else:
            print("Link Arturo-Elvira already exists")

        # 7. Generate Reports for ALL Students in this School (Green-Orange)
        print("\nUsing School: " + school.name)
        from app.models import SurveyResponse, AlertLevel
        from app.agents.predictor import heuristic_engine
        from app.schemas import SurveyInput
        import json
        from datetime import datetime
        
        all_students = db.query(Student).filter(Student.school_id == school.id).all()
        print(f"Generating reports for {len(all_students)} students...")
        
        for s in all_students:
            # Check if survey exists
            existing = db.query(SurveyResponse).filter(SurveyResponse.student_id == s.id).first()
            if existing:
                db.delete(existing) 
                db.commit()
            
            # Decide Risk: 70% Low (Green), 30% Medium/High (Orange)
            roll = random.random()
            
            answers = {}
            if roll < 0.7:
                # LOW RISK PROFILE
                # Mostly 0s
                answers = {
                    "p_item_1": 0, "p_item_2": 0, "p_item_3": 0, "p_item_4": 0, "p_item_5": 0,
                    "p_item_6": 0, "p_item_7": 0, "p_item_8": 0, "p_item_9": 0, "p_item_10": 0,
                    "p_item_11": 0, "p_item_12": 0, "p_item_13": 0,
                    "p_observations": "Sin novedad."
                }
                # Random noise (safe)
                if random.random() < 0.2:
                    answers["p_item_8"] = 1 
            
            elif roll < 0.9:
                # MEDIUM RISK PROFILE
                # Some 1s and 2s
                answers = {
                    "p_item_1": 0, 
                    "p_item_2": 0,
                    "p_item_3": random.randint(0, 1),
                    "p_item_4": 0,
                    "p_item_5": 0,
                    "p_item_6": random.randint(1, 2), # Ansiedad mañana
                    "p_item_7": random.randint(1, 2), # Dolores físicos
                    "p_item_8": random.randint(2, 3), # Sueño/Alimentación
                    "p_item_9": random.randint(1, 2), # Humor
                    "p_item_10": random.randint(1, 2), # Evitación
                    "p_item_11": 0,
                    "p_item_12": 0,
                    "p_item_13": 0,
                    "p_observations": "Le cuesta levantarse por las mañanas."
                }
            else:
                # HIGH RISK PROFILE
                # Higher values
                answers = {
                    "p_item_1": 0, 
                    "p_item_2": 0,
                    "p_item_3": random.randint(1, 2),
                    "p_item_4": random.randint(1, 2),
                    "p_item_5": 0,
                    "p_item_6": random.randint(3, 4), # Ansiedad mañana
                    "p_item_7": random.randint(2, 3), # Dolores físicos
                    "p_item_8": random.randint(3, 4), # Sueño
                    "p_item_9": random.randint(2, 3), # Humor
                    "p_item_10": random.randint(2, 4), # Evitación
                    "p_item_11": random.randint(0, 1),
                    "p_item_12": 0,
                    "p_item_13": 0,
                    "p_observations": "Ha dejado de comer bien y llora a menudo."
                }

            # Calculate logic score based on answers
            survey_input = SurveyInput(**answers)
            analysis = heuristic_engine.analyze(survey_input)
            
            # Force Green/Orange limit (avoid Critical Red)
            # If critical, downgrade slightly
            if analysis.risk_level == "Critical":
                # Manual downgrade to avoid Red as per user request
                score = 25 
                risk = AlertLevel.HIGH
                # But keep analysis flags
            else:
                score = analysis.total_score
                risk = AlertLevel(analysis.risk_level)

            survey = SurveyResponse(
                submitted_by_id=parent.id, 
                student_id=s.id,
                raw_answers=json.dumps(answers),
                calculated_risk_score=score,
                risk_level=risk,
                ai_summary=analysis.recommendation, # Use engine recommendation
                date_submitted=datetime.utcnow()
            )
            db.add(survey)
        
        db.commit()
        print(f"Reports generated/verified for {len(all_students)} students.")

        print("\n=== SCENARIO READY ===")
        print(f"School: {school.name} ({school.center_code})")
        print("Director: laura@hotmail.com / 123456")
        print("Teacher:  meferal@hotmail.com / 123456 (Class: 4º ESO A, 25 Students)")
        print(f"Student:  Elvira (Age 16)")
        print("Parent:   arturo@hotmail.com / 123456 (Linked to Elvira)")
        print("======================")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_custom_scenario()
