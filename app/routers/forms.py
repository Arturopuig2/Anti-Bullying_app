from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import SurveyInput, RiskAnalysisResult
from ..agents.predictor import heuristic_engine
from ..models import SurveyResponse, AlertLevel, User, Student
from ..security import get_current_user
import json

router = APIRouter(prefix="/surveys", tags=["surveys"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/parent", response_class=HTMLResponse)
def get_parent_survey(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("forms/parent_survey.html", {
        "request": request,
        "user": current_user
    })

from fastapi import BackgroundTasks
from ..agents.incident_responder import incident_responder

@router.post("/api/submit", response_model=RiskAnalysisResult)
def submit_survey(
    survey_data: SurveyInput, 
    student_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id
    # 1. Verificar existencia (Básico)
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 2. Calcular Sentimiento del Profesor (Contexto)
    teacher_sentiment = 0.0
    if student.teacher_id:
        from ..models import ClassObservation
        from ..utils.text_analysis import calculate_atmosphere_score
        
        # Últimas 5 observaciones
        observations = db.query(ClassObservation)\
            .filter(ClassObservation.teacher_id == student.teacher_id)\
            .order_by(ClassObservation.timestamp.desc())\
            .limit(5).all()
        
        teacher_sentiment = calculate_atmosphere_score(observations)

    # 3. Análisis del Agente
    analysis = heuristic_engine.analyze(survey_data, teacher_sentiment)
    
    # 3. Persistencia en BD
    db_survey = SurveyResponse(
        submitted_by_id=user_id,
        student_id=student_id,
        raw_answers=survey_data.model_dump_json(),
        calculated_risk_score=analysis.total_score,
        risk_level=AlertLevel(analysis.risk_level), # Convertir string a Enum
        ai_summary=analysis.recommendation
    )
    
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    
    # 4. Invocación al Agente de Respuesta (Si es necesario)
    if analysis.risk_level in ["high", "critical"] and student.teacher_id:
        # Recuperar email del profesor
        teacher_email = "profesor_demo@colegio.com"
        if student.teacher and student.teacher.email:
             teacher_email = student.teacher.email
             
        background_tasks.add_task(
            incident_responder.handle_alert, 
            student, 
            analysis, 
            teacher_email
        )
    
    return analysis

# --- Teacher Routes ---

@router.get("/teacher/student-report", response_class=HTMLResponse)
def teacher_select_student_page(request: Request, current_user: User = Depends(get_current_user)):
    from ..models import UserRole
    if current_user.role not in [UserRole.TEACHER, UserRole.SCHOOL_ADMIN]:
         return templates.TemplateResponse("error.html", {"request": request, "error": "Acceso restringido a docentes."})
    
    # Listar alumnos asignados
    return templates.TemplateResponse("forms/student_select.html", {
        "request": request,
        "user": current_user,
        "students": current_user.supervised_students
    })

@router.get("/teacher/student-report/form", response_class=HTMLResponse)
def teacher_fill_survey_page(request: Request, student_id: int, current_user: User = Depends(get_current_user)):
    # Reutilizamos el formulario de padres, pero inyectamos el student_id seleccionado
    # Validar que el alumno pertenece al profesor
    authorized = any(s.id == student_id for s in current_user.supervised_students)
    if not authorized:
         return templates.TemplateResponse("error.html", {"request": request, "error": "Este alumno no está asignado a tu clase."})

    return templates.TemplateResponse("forms/teacher_survey.html", {
        "request": request,
        "user": current_user,
        "student_id": student_id
    })

@router.get("/teacher/class-report", response_class=HTMLResponse)
def teacher_class_report_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("forms/class_report.html", {
        "request": request,
        "user": current_user
    })

@router.post("/teacher/class-report", response_class=HTMLResponse)
def teacher_class_report_submit(
    request: Request, 
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from ..models import ClassObservation
    
    observation = ClassObservation(
        teacher_id=current_user.id,
        content=content
    )
    db.add(observation)
    db.commit()
    
    return templates.TemplateResponse("forms/class_report.html", {
        "request": request, 
        "user": current_user,
        "message": "Informe de clase registrado correctamente."
    })
