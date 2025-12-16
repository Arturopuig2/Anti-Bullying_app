import json
import joblib
import pandas as pd
import shap
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from .models import SurveyResponse, AlertLevel, ClassObservation, User, Student
from .database import engine
from .utils.text_analysis import calculate_atmosphere_score

MODEL_PATH = "model.pkl"

def load_data(db: Session):
    surveys = db.query(SurveyResponse).filter(SurveyResponse.raw_answers.isnot(None)).all()
    data = []
    
    for s in surveys:
        try:
            answers = json.loads(s.raw_answers)
            # Flatten features
            row = {}
            # Items 1-13
            for i in range(1, 14):
                row[f'p_item_{i}'] = int(answers.get(f'p_item_{i}', 0))
                
            # --- NEW: Teacher Context ---
            # Find the teacher associated with the student AT THE TIME
            # (Simplification: Use current teacher observations)
            teacher_sentiment = 0.0
            if s.student and s.student.teacher_id:
                # Get observations from THAT teacher
                # Ideal: Filter by date range near survey. Simplification: Last 5.
                observations = db.query(ClassObservation)\
                    .filter(ClassObservation.teacher_id == s.student.teacher_id)\
                    .order_by(ClassObservation.timestamp.desc())\
                    .limit(5).all()
                    
                teacher_sentiment = calculate_atmosphere_score(observations)
            
            row['teacher_sentiment'] = teacher_sentiment
            # ----------------------------
            
            # Target Determination
            # 1. Expert Label Overrides everything
            if s.expert_label == "real_case":
                target = 1
            elif s.expert_label == "false_positive":
                target = 0
            elif s.expert_label == "false_negative":
                target = 1 
            else:
                # 2. Heuristic fallback
                if s.risk_level in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
                    target = 1
                else:
                    target = 0
            
            row['target'] = target
            data.append(row)
        except:
            continue
            
    return pd.DataFrame(data)

def train_model():
    with Session(engine) as db:
        df = load_data(db)
    
    if df.empty:
        print("No data to train.")
        return False

    X = df.drop(columns=['target'])
    y = df['target']
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    joblib.dump(clf, MODEL_PATH)
    print(f"Model trained on {len(df)} samples.")
    return True

def predict_risk(answers_dict, teacher_sentiment=0.0):
    """
    Returns (probability, explanation_text)
    """
    try:
        clf = joblib.load(MODEL_PATH)
    except:
        return 0.0, "Model not trained yet."
    
    # Prepare features
    features = {}
    for i in range(1, 14):
        features[f'p_item_{i}'] = [int(answers_dict.get(f'p_item_{i}', 0))]
        
    # Add new feature
    features['teacher_sentiment'] = [teacher_sentiment]
    
    X_new = pd.DataFrame(features)
    
    # Predict Proba Robustness
    if hasattr(clf, "classes_") and len(clf.classes_) > 1:
        prob = clf.predict_proba(X_new)[0][1] # Probability of Class 1
    else:
        # If model only knows one class
        if hasattr(clf, "classes_") and clf.classes_[0] == 1:
            prob = 1.0
        else:
            prob = 0.0
    
    # SAFETY NETS (Reglas de Oro)
    # Item 2: Heridas o moratones (Physical violence) -> Force Critical
    # Item 5: Coacción o amenazas (Threats) -> Force High
    
    explanation_prefix = ""
    if features['p_item_2'][0] >= 3: # 3 or 4 means Often/Always
        prob = 1.0
        explanation_prefix = "[SAFETY NET] Physical violence detected (Item 2). Risk set to Critical. "
    elif features['p_item_5'][0] >= 3:
        if prob < 0.8: prob = 0.8 # Ensure at least High risk
        explanation_prefix = "[SAFETY NET] Severe threats detected (Item 5). Risk elevated. "
    
    # Explainability (SHAP)
    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X_new)
    
    # SHAP Robustness: Handle different return shapes
    # Binary classification: [array_class_0, array_class_1] or just array_class_1 depending on version
    vals = None
    if isinstance(shap_values, list) and len(shap_values) > 1:
        vals = shap_values[1][0] # Class 1
    elif isinstance(shap_values, list) and len(shap_values) == 1:
         # Only one class explained?
         vals = shap_values[0][0]
    else:
         # Sometimes it returns a single array if binary
         if hasattr(shap_values, 'shape') and len(shap_values.shape) == 2:
             vals = shap_values[0] # (1, features)
         else:
             # Fallback
             vals = [0] * len(X_new.columns)

    feature_names = X_new.columns
    
    # Sort by absolute impact
    indices = sorted(range(len(vals)), key=lambda k: abs(vals[k]), reverse=True)
    
    top_reasons = []
    for i in indices[:3]:
        if vals[i] > 0: # Only list things that INCREASED risk
            top_reasons.append(f"{feature_names[i]} ({vals[i]:.2f})")
            
    explanation = explanation_prefix + ("Risk factors: " + ", ".join(top_reasons) if top_reasons else "Low risk factors detected.")
    
    return prob, explanation
