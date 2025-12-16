
import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import School, User, Student, SurveyResponse, ClassObservation

def delete_fake_data():
    db = SessionLocal()
    try:
        # Find Fake Schools
        fake_schools = db.query(School).filter(School.address.like("%Calle Falsa%")).all()
        print(f"Found {len(fake_schools)} schools with 'Calle Falsa'.")
        
        for school in fake_schools:
            print(f"Deleting School: {school.name}...")
            
            # 1. Delete Students and their Surveys
            students = db.query(Student).filter(Student.school_id == school.id).all()
            for s in students:
                # Delete Surveys
                db.query(SurveyResponse).filter(SurveyResponse.student_id == s.id).delete()
            
            # Delete Students
            db.query(Student).filter(Student.school_id == school.id).delete()
            
            # 2. Delete Teachers/Users and their Observations
            users = db.query(User).filter(User.school_id == school.id).all()
            for u in users:
                # Delete Observations
                db.query(ClassObservation).filter(ClassObservation.teacher_id == u.id).delete()
                
            # Delete Users
            db.query(User).filter(User.school_id == school.id).delete()
            
            # 3. Delete School
            db.delete(school)
            
        db.commit()
        print("Deletion Complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_fake_data()
