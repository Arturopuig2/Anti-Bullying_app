
@router.get("/super_admin/school/{school_id}", response_class=HTMLResponse)
def view_school_detail_as_admin(request: Request, school_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.SUPER_ADMIN:
         return templates.TemplateResponse("error.html", {"request": request, "error": "Acceso restringido."})
    
    from ..models import School, Student, SurveyResponse, AlertLevel
    from collections import defaultdict

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
         return templates.TemplateResponse("error.html", {"request": request, "error": "Centro no encontrado."})

    # Reuse logic from school_admin_dashboard
    # 1. Obtener todos los alumnos del centro
    students = db.query(Student).filter(Student.school_id == school.id).all()
    
    # 2. Agrupar por Aula
    classrooms = defaultdict(lambda: {"students": [], "alerts": 0, "status": "green"})
    total_alerts_global = 0
    
    for s in students:
        c_name = s.grade_class if s.grade_class else "Sin Asignar"
        classrooms[c_name]["students"].append(s)
        
        # Check high risk surveys
        high_risk_surveys = db.query(SurveyResponse).filter(
            SurveyResponse.student_id == s.id,
            SurveyResponse.risk_level.in_([AlertLevel.HIGH, AlertLevel.CRITICAL])
        ).count()
        
        classrooms[c_name]["alerts"] += high_risk_surveys
        total_alerts_global += high_risk_surveys

    # 3. Determinar Estado por Aula
    classroom_list = []
    
    for name, data in classrooms.items():
        count = len(data["students"])
        alerts = data["alerts"]
        
        critical_count = db.query(SurveyResponse).join(Student).filter(
            Student.grade_class == name,
            Student.school_id == school.id,
            SurveyResponse.risk_level == AlertLevel.CRITICAL
        ).count()

        has_critical = critical_count > 0

        # Status Logic
        status_color = "green"
        if has_critical:
            status_color = "red"
        elif alerts > 0:
            status_color = "orange"
            
        classroom_list.append({
            "name": name,
            "student_count": count,
            "alerts_count": alerts,
            "status": status_color,
            "has_critical": has_critical
        })
        
    classroom_list.sort(key=lambda x: x["alerts_count"], reverse=True)

    # Estado Global
    school_status = "Saludable"
    school_color = "green"
    if any(c["status"] == "red" for c in classroom_list):
        school_status = "Riesgo Alto Detectado"
        school_color = "red"
    elif any(c["status"] == "orange" for c in classroom_list):
        school_status = "Precaución"
        school_color = "orange"

    return templates.TemplateResponse("dashboard/school_admin_view.html", {
        "request": request,
        "user": current_user,
        "school": school,
        "total_students": len(students),
        "total_alerts": total_alerts_global,
        "school_status": school_status,
        "school_color": school_color,
        "classrooms": classroom_list
    })
