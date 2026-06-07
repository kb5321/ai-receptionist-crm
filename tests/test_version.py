from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_version():

    response = client.get("/version")

    assert response.status_code == 200

    data = response.json()

    assert "version" in data
    assert "app" in data