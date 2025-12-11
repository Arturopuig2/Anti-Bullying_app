from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime
import enum

class Base(DeclarativeBase):
    pass

# --- ENUMS para Roles y Estados ---
class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"  # Dios del sistema
    SCHOOL_ADMIN = "school_admin" # Director/Psicólogo del centro
    TEACHER = "teacher"
    PARENT = "parent"

class AlertLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical" # Dispara notificación inmediata

# --- TABLAS ---

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    address = Column(String)
    contact_email = Column(String) # Email para alertas críticas del centro
    is_active = Column(Boolean, default=True)
    
    users = relationship("User", back_populates="school")
    students = relationship("Student", back_populates="school")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole))
    
    # Recuperación de contraseña
    recovery_token = Column(String, nullable=True)

    # Código único del profesor (9 caracteres) - Solo si role=TEACHER/SCHOOL_ADMIN
    teacher_code = Column(String(9), unique=True, index=True, nullable=True)

    # Multi-tenancy: A qué colegio pertenece (Null si es SuperAdmin global)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    school = relationship("School", back_populates="users")
    
    # Relación Padre -> Hijos (Muchos a Muchos)
    children = relationship("Student", secondary="parent_student_link", back_populates="parents")
    
    # Relación Profesor -> Alumnos (Uno a Muchos) - Alumnos que supervisa este profesor
    supervised_students = relationship("Student", back_populates="teacher", foreign_keys="Student.teacher_id")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    internal_code = Column(String, unique=True, index=True) 
    age = Column(Integer)
    grade_class = Column(String) 
    
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    school = relationship("School", back_populates="students")
    
    # Profesor asignado
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    teacher = relationship("User", back_populates="supervised_students", foreign_keys=[teacher_id])
    
    parents = relationship("User", secondary="parent_student_link", back_populates="children")
    surveys = relationship("SurveyResponse", back_populates="student")

# Tabla intermedia para relacionar Padres y Alumnos (Muchos a Muchos)
class ParentStudentLink(Base):
    __tablename__ = "parent_student_link"
    parent_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)

class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    id = Column(Integer, primary_key=True, index=True)
    date_submitted = Column(DateTime, default=datetime.utcnow)
    
    # Quién rellenó la encuesta
    submitted_by_id = Column(Integer, ForeignKey("users.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    
    # Datos crudos (JSON) y Análisis
    raw_answers = Column(Text) # JSON con las respuestas del formulario
    
    # Resultado del Análisis Heurístico / ML
    calculated_risk_score = Column(Integer) # 0 a 100
    risk_level = Column(Enum(AlertLevel))
    ai_summary = Column(Text) # Resumen generado por LangChain
    
    student = relationship("Student", back_populates="surveys")
