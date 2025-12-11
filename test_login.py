from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_flow():
    # 1. Intentar hacer login con credenciales correctas
    print("Probando Login Correcto...")
    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "secreto123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token is not None
    
    # 2. Intentar hacer login con credenciales incorrectas
    print("\nProbando Login Incorrecto...")
    response_bad = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "wrong_password"}
    )
    print(f"Status: {response_bad.status_code}")
    assert response_bad.status_code == 401

if __name__ == "__main__":
    try:
        test_login_flow()
        print("\nSUCCESS: Sistema de Login verificado.")
    except Exception as e:
        print(f"\nERROR: {e}")
