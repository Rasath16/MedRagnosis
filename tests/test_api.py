from fastapi.testclient import TestClient
from server.main import app 

client = TestClient(app)

# 1. Test Health Check
def test_health_check():
    """Ensure the API is up and running"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}

# 2. Test Signup Validation (Fail Case)
def test_signup_missing_fields():
    """Should fail if password is missing"""
    response = client.post("/auth/signup", json={
        "username": "test_incomplete",
        "role": "patient"
    })
    assert response.status_code == 422 

# 3. Test Login (Fail Case)
def test_login_invalid_user():
    """Should fail for non-existent user"""
    response = client.post("/auth/login", json={
        "username": "ghost_user",
        "password": "wrong_password",
        "role": "patient"
    })
  
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"