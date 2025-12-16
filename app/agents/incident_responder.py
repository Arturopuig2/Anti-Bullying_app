from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class IncidentResponder:
    """
    Agente especializado en Respuesta a Incidentes (Incident Response).
    Su objetivo es orquestar la reacción ante una alerta crítica:
    1. Generar un Plan de Acción Inmediato (basado en la alerta).
    2. Notificar a las partes responsables (Profesor/Dirección).
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        
        # Prompt especializado en protocolos de actuación
        self.plan_prompt = ChatPromptTemplate.from_template(
            """
            Actúas como un Coordinador de Bienestar y Protección del Menor.
            Se ha detectado una ALERTA DE NIVEL: {risk_level} para el alumno {student_code}.
            
            Indicadores detectados:
            {flags}
            
            Resumen del análisis inicial:
            {ai_summary}
            
            Genera un PLAN DE ACCIÓN INMEDIATO (Email formal) dirigido al Profesor Tutor.
            El email debe incluir:
            1. Asunto Urgente.
            2. Resumen de los hechos.
            3. Lista de 3 pasosa seguir en las próximas 24 horas (basado en protocolos anti-acoso estándar).
            4. Tono profesional, urgente pero calmado.
            
            Firma como: Agente de Respuesta a Incidentes - Sistema Anti-Bullying.
            """
        )
        
        self.chain = self.plan_prompt | self.llm | StrOutputParser()

    def handle_alert(self, student, risk_analysis, teacher_email: str):
        """
        Método principal que orquesta la respuesta.
        """
        print(f"🚨 [INCIDENT AGENT] Activado para estudiante {student.internal_code}")
        
        # 1. Generar Plan con LLM
        action_plan_email = self.chain.invoke({
            "risk_level": risk_analysis.risk_level,
            "student_code": student.internal_code,
            "flags": ", ".join(risk_analysis.flags),
            "ai_summary": risk_analysis.recommendation
        })
        
        # 2. Enviar Notificación (Simulada)
        self._send_email(teacher_email, action_plan_email)
        
        return action_plan_email

    def _send_email(self, to_email: str, content: str):
        # Enviar correo real usando utilidad SMTP
        try:
            from ..utils.email import send_email
            # Extract basic subject or use default
            subject = "🚨 ALERTA ANTIBULLYING: Acción Requerida"
            
            # Convierte saltos de linea a <br> para HTML básico si es texto plano
            html_content = content.replace("\n", "<br>")
            
            send_email(to_email, subject, html_content)
            
        except Exception as e:
            print(f"❌ Error enviando email SMTP: {e}")

        # Log en terminal (solicitado por usuario)
        print(f"\n📨 [EMAIL SENT] To: {to_email}")
        print("---------------------------------------------------")
        print(content)
        print("---------------------------------------------------\n")

incident_responder = IncidentResponder()
