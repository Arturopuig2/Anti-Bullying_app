from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import SurveyInput, RiskAnalysisResult
from ..agents.predictor import heuristic_engine
from ..models import SurveyResponse, AlertLevel, User, Student
import json

router = APIRouter(prefix="/surveys", tags=["surveys"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/parent", response_class=HTMLResponse)
def get_parent_survey(request: Request):
    return templates.TemplateResponse("forms/parent_survey.html", {"request": request})

from ..security import get_current_user

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

    # 2. Análisis del Agente
    analysis = heuristic_engine.analyze(survey_data)
    
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
        # Recuperar email del profesor (o usar dummy si no tiene)
        teacher_email = "profesor_demo@colegio.com" # TODO: student.teacher.email
        background_tasks.add_task(
            incident_responder.handle_alert, 
            student, 
            analysis, 
            teacher_email
        )
    
    return analysis
