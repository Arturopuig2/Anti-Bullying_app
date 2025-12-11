from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..database import get_db
from ..models import Student, SurveyResponse, AlertLevel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")

from ..security import get_current_user
from ..models import User, UserRole

@router.get("/teacher", response_class=HTMLResponse)
def teacher_dashboard(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verificar rol
    if current_user.role not in [UserRole.TEACHER, UserRole.SCHOOL_ADMIN]:
         return templates.TemplateResponse("error.html", {"request": request, "error": "Acceso restringido a profesores."})
    
    teacher = current_user

    # 1. Obtener métricas generales (SOLO de sus alumnos asignados)
    total_students = db.query(Student).filter(Student.teacher_id == teacher.id).count()
    
    # 2. Buscar alertas recientes (Riesgo Alto o Crítico) DE SUS ALUMNOS
    critical_alerts = db.query(SurveyResponse).join(Student).filter(
        Student.teacher_id == teacher.id,
        SurveyResponse.risk_level.in_([AlertLevel.HIGH, AlertLevel.CRITICAL])
    ).order_by(desc(SurveyResponse.date_submitted)).all()
    
    # 3. Datos para la tabla principal (Últimas encuestas) DE SUS ALUMNOS
    recent_activity = db.query(SurveyResponse).join(Student).filter(
        Student.teacher_id == teacher.id
    ).order_by(desc(SurveyResponse.date_submitted)).limit(20).all()
    
    # 4. Calcular Estadísticas Reales
    # Porcentaje de encuestas "Saludables" (LOW Risk) recientes
    total_surveys = len(recent_activity)
    healthy_count = sum(1 for s in recent_activity if s.risk_level == AlertLevel.LOW)
    healthy_percentage = int((healthy_count / total_surveys * 100)) if total_surveys > 0 else 100

    return templates.TemplateResponse("dashboard/teacher_view.html", {
        "request": request,
        "teacher": teacher, 
        "total_students": total_students,
        "critical_count": len(critical_alerts),
        "healthy_percentage": healthy_percentage,
        "alerts": critical_alerts,
        "activity": recent_activity
    })

@router.get("/case/{survey_id}", response_class=HTMLResponse)
def view_case_details(request: Request, survey_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validar rol
    if current_user.role not in [UserRole.TEACHER, UserRole.SCHOOL_ADMIN]:
         return templates.TemplateResponse("error.html", {"request": request, "error": "No autorizado"})
    
    survey = db.query(SurveyResponse).filter(SurveyResponse.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
        
    # Validar que el alumno pertenece al profe (opcional, pero recomendado)
    if survey.student.teacher_id != current_user.id:
         return templates.TemplateResponse("error.html", {"request": request, "error": "Este caso no pertenece a tus alumnos asignados"})
         
    return templates.TemplateResponse("dashboard/case_details.html", {"request": request, "survey": survey})
