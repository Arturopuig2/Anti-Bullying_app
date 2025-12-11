from ..schemas import SurveyInput, RiskAnalysisResult, Frequency, YesNo
from ..models import AlertLevel

class HeuristicPredictor:
    """
    Motor de análisis basado en reglas (Adaptación TEBAE).
    Calcula el riesgo basándose en pesos predefinidos ante la falta de datos históricos.
    """
    
    # Pesos de configuración
    SCORE_MAP = {
        Frequency.NEVER: 0,
        Frequency.SOMETIMES: 1,
        Frequency.OFTEN: 2,
        Frequency.ALWAYS_CORRECTED: 3
    }

    # Umbrales
    THRESHOLD_CRITICAL = 12 # Puntuación muy alta
    THRESHOLD_HIGH = 8
    THRESHOLD_MEDIUM = 4

    def analyze(self, data: SurveyInput) -> RiskAnalysisResult:
        score = 0
        flags = []
        
        # 1. Análisis Psicosomático (Peso Normal)
        score += self.SCORE_MAP.get(data.headache_stomach, 0)
        
        # 2. Análisis Conductual (Peso Normal)
        score += self.SCORE_MAP.get(data.mood_changes, 0)
        score += self.SCORE_MAP.get(data.sleep_problems, 0)
        score += self.SCORE_MAP.get(data.school_resistance, 0)
        
        # 3. Indicadores Directos (Peso Alto / Trigger Inmediato)
        if data.damaged_items == YesNo.YES:
            score += 5 # Penalización alta
            flags.append("Material escolar dañado o perdido")
            
        if data.conflict_verbalized == YesNo.YES:
            score += 5
            flags.append("Conflicto verbalizado explícitamente")

        # Determinación de Nivel de Riesgo
        risk_level = AlertLevel.LOW
        
        # Lógica de "Muerte Súbita" (Indicadores graves disparan riesgo alto inmediatamente)
        if score >= self.THRESHOLD_CRITICAL or (data.damaged_items == YesNo.YES and data.conflict_verbalized == YesNo.YES):
             risk_level = AlertLevel.CRITICAL
        elif score >= self.THRESHOLD_HIGH:
             risk_level = AlertLevel.HIGH
        elif score >= self.THRESHOLD_MEDIUM:
             risk_level = AlertLevel.MEDIUM
             
        # Recomendación básica (será enriquecida luego por el RAG)
        recommendation = self._get_recommendation(risk_level)

        return RiskAnalysisResult(
            total_score=score,
            risk_level=risk_level.value,
            flags=flags,
            recommendation=recommendation
        )

    def _get_recommendation(self, level: AlertLevel) -> str:
        if level == AlertLevel.CRITICAL:
            return "ALERTA: Se detectan indicadores graves. Se requiere intervención inmediata del centro."
        elif level == AlertLevel.HIGH:
            return "Riesgo Alto: Se observan patrones preocupantes consistentes. Recomendamos solicitar tutoría."
        elif level == AlertLevel.MEDIUM:
            return "Precaución: Mantener observación. Hay indicadores de malestar."
        else:
            return "Sin riesgo apreciable actualmente. Continuar monitorización normal."

heuristic_engine = HeuristicPredictor()
