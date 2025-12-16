
from typing import List
from ..models import ClassObservation

POSITIVE_KEYWORDS = ["normal", "bien", "tranquilo", "positivo", "mejora", "adecuado", "colaborativo"]
NEGATIVE_KEYWORDS = ["conflicto", "agresión", "pelea", "insulto", "rumor", "amenaza", "bullying", "acoso", "golpe", "llanto", "miedo", "aislado"]

def calculate_atmosphere_score(observations: List[ClassObservation]) -> float:
    """
    Calculates a 'Negative Atmosphere Score' from 0.0 (Good) to 1.0 (Bad).
    Based on recent teacher observations.
    """
    if not observations:
        return 0.0
    
    total_score = 0
    count = 0
    
    for obs in observations:
        content = obs.content.lower()
        
        # Simple negative keyword count
        neg_count = sum(1 for k in NEGATIVE_KEYWORDS if k in content)
        pos_count = sum(1 for k in POSITIVE_KEYWORDS if k in content)
        
        # Row score: -1 (Good) to +N (Bad)
        # We want to normalize to 0..1 eventually for the whole set
        
        # Heuristic: 
        # If neg > 0 -> Risk increases
        # If pos > neg -> Risk decreases (or stays 0)
        
        row_risk = 0.0
        if neg_count > 0:
            row_risk = 0.2 + (neg_count * 0.1) # Base risk + severity
        elif pos_count > 0:
            row_risk = 0.0
        else:
            row_risk = 0.05 # Uncertainty / Neutral
            
        total_score += row_risk
        count += 1
        
    avg_score = total_score / count
    
    # Cap at 1.0
    return min(avg_score, 1.0)
