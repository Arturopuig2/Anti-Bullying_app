from app.schemas import SurveyInput, Frequency, YesNo
from app.agents.predictor import heuristic_engine

def test_logic():
    print("--- Test 1: Caso Sin Riesgo ---")
    case_safe = SurveyInput(
        headache_stomach=Frequency.NEVER,
        mood_changes=Frequency.NEVER,
        sleep_problems=Frequency.NEVER,
        school_resistance=Frequency.SOMETIMES,
        damaged_items=YesNo.NO,
        conflict_verbalized=YesNo.NO
    )
    result = heuristic_engine.analyze(case_safe)
    print(f"Score: {result.total_score}, Level: {result.risk_level}")
    assert result.risk_level == "low"

    print("\n--- Test 2: Caso Riesgo Medio ---")
    case_medium = SurveyInput(
        headache_stomach=Frequency.OFTEN, # 2
        mood_changes=Frequency.OFTEN, # 2
        sleep_problems=Frequency.SOMETIMES, # 1
        school_resistance=Frequency.NEVER,
        damaged_items=YesNo.NO,
        conflict_verbalized=YesNo.NO
    )
    # Total 5 -> Medium (>4)
    result = heuristic_engine.analyze(case_medium)
    print(f"Score: {result.total_score}, Level: {result.risk_level}")
    assert result.risk_level == "medium"

    print("\n--- Test 3: Caso Crítico (Violencia Directa) ---")
    case_critical = SurveyInput(
        headache_stomach=Frequency.NEVER,
        mood_changes=Frequency.NEVER,
        sleep_problems=Frequency.NEVER,
        school_resistance=Frequency.NEVER,
        damaged_items=YesNo.YES, # +5
        conflict_verbalized=YesNo.YES # +5
    )
    # Total 10, pero trigger de ambos flags -> Critical
    result = heuristic_engine.analyze(case_critical)
    print(f"Score: {result.total_score}, Level: {result.risk_level}, Flags: {result.flags}")
    assert result.risk_level == "critical"

if __name__ == "__main__":
    try:
        test_logic()
        print("\nSUCCESS: Lógica verificada correctamente.")
    except Exception as e:
        print(f"\nERROR: {e}")
