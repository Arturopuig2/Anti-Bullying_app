from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, Base, engine
from app.models import School, User, Student, UserRole, SurveyResponse

# Setup DB para Tests
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def setup_data():
    db = next(get_db())
    # 1. Crear Escuela
    school = School(name="Colegio Test", address="Calle Falsa 123", contact_email="admin@test.com")
    db.add(school)
    db.commit()
    
    # 2. Crear Padre
    parent = User(email="padre@test.com", role=UserRole.PARENT, school_id=school.id, full_name="Juan Perez")
    db.add(parent)
    db.commit()
    
    # 3. Crear Alumno
    student = Student(internal_code="ST-001", age=14, grade_class="3 ESO", school_id=school.id)
    db.add(student)
    db.commit()
    
    return parent.id, student.id

def test_submission():
    parent_id, student_id = setup_data()
    
    payload = {
        "headache_stomach": "a_menudo",
        "mood_changes": "a_menudo",
        "sleep_problems": "nunca",
        "school_resistance": "a_veces",
        "damaged_items": "no",
        "conflict_verbalized": "no",
        "conflict_details": ""
    }
    
    # Enviar POST con IDs simulados en query params
    response = client.post(f"/api/surveys/submit?student_id={student_id}&user_id={parent_id}", json=payload)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "medium"
    
    # Verificar BD
    db = next(get_db())
    saved_survey = db.query(SurveyResponse).first()
    print(f"Saved in DB Risk Level: {saved_survey.risk_level}")
    assert saved_survey.risk_level.value == "medium"
    assert saved_survey.student_id == student_id

if __name__ == "__main__":
    try:
        test_submission()
        print("\nSUCCESS: Integración BD verificada.")
    except Exception as e:
        print(f"\nERROR: {e}")
