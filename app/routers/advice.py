from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..agents.rag_expert import rag_system

router = APIRouter(prefix="/advice", tags=["advice"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

from ..security import get_current_user, User
from ..models import UserRole

@router.get("/ask")
def ask_expert(query: str, current_user: User = Depends(get_current_user)):
    """
    Endpoint para preguntar al RAG.
    Rol determinado automáticamente por el login.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query vacía")
    
    # Mapear rol del usuario al rol del RAG
    # Si es PARENT -> parents
    # Si es TEACHER o SCHOOL_ADMIN -> teachers
    rag_role = "parents"
    if current_user.role in [UserRole.TEACHER, UserRole.SCHOOL_ADMIN, UserRole.SUPER_ADMIN]:
        rag_role = "teachers"

    response = rag_system.get_advice(query, rag_role)
    return {"response": response, "role_used": rag_role}
