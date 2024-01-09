from fastapi.testclient import TestClient
from src.main  import app

client = TestClient(app)

def test_app():
    response = client.get("/auth")
    assert response.status_code == 200
    assert response.json() == {"name": "ob-sample-fast-api", "version": "1.0.0"}

