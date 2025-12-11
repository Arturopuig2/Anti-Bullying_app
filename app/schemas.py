from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# --- ENUMS para las Respuestas ---
class Frequency(str, Enum):
    NEVER = "nunca"
    SOMETIMES = "a_veces"
    OFTEN = "a_menudo"
    ALWAYS = "sempre" # Typo intention check? No, standardizing to spanish: siempre
    ALWAYS_CORRECTED = "siempre"

class YesNo(str, Enum):
    YES = "si"
    NO = "no"

# --- Schema del Formulario (Input) ---
class SurveyInput(BaseModel):
    # A. Sintomatología Psicosomática
    headache_stomach: Frequency = Field(..., description="Dolores de cabeza o estómago antes de ir al colegio")
    
    # B. Cambios Conductuales / Emocionales
    mood_changes: Frequency = Field(..., description="Cambios bruscos de humor o irritabilidad")
    sleep_problems: Frequency = Field(..., description="Dificultades para dormir o pesadillas")
    school_resistance: Frequency = Field(..., description="Resistencia o ansiedad al ir al colegio")
    
    # C. Indicadores Directos
    damaged_items: YesNo = Field(..., description="Material roto o perdido")
    conflict_verbalized: YesNo = Field(..., description="Ha contado conflictos verbalmente")
    conflict_details: Optional[str] = Field(None, description="Detalles del conflicto si existen")

# --- Schema del Resultado (Output del Agente) ---
class RiskAnalysisResult(BaseModel):
    total_score: int
    risk_level: str # Low, Medium, High, Critical
    flags: List[str] # Lista de alertas específicas (ej: "Daño material detectado")
    recommendation: str

# --- Schemas de Usuario ---
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str

class StudentCreate(BaseModel):
    name: str # En modelo real es 'internal_code' pero usaremos esto como display
    age: int
    grade: str # Clase/Curso
    school_name: str # Nombre del colegio (lo buscaremos u crearemos)
