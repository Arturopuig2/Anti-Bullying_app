from app.security import validate_password_strength
from fastapi import HTTPException

def test_policy():
    print("Testing Password Policy...")
    
    # Casos Fallidos
    weak_passwords = [
        "short", # < 10
        "lownumbersymbol1!", # No Upper
        "UPPERNUMBERSYMBOL1!", # No Lower (Wait, rules didn't say lower, but standard)
        "UpperNoSymbol1", # No Symbol
        "UpperSymbol!", # No Number
    ]
    
    for pwd in weak_passwords:
        try:
            validate_password_strength(pwd)
            print(f"FAILED: '{pwd}' should have raised error")
        except HTTPException as e:
            print(f"SUCCESS: '{pwd}' rejected -> {e.detail}")

    # Caso Exitoso
    strong_pwd = "StrongPassword1!"
    try:
        validate_password_strength(strong_pwd)
        print(f"SUCCESS: '{strong_pwd}' accepted")
    except Exception as e:
        print(f"FAILED: '{strong_pwd}' rejected incorrectly: {e}")

if __name__ == "__main__":
    test_policy()
