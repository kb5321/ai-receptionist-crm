import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from main import app

client = TestClient(app)


def test_get_appointments():
    response = client.get("/appointments")

    assert response.status_code == 200

    data = response.json()

    assert "total_appointments" in data
    assert "appointments" in data
    assert isinstance(data["appointments"], list)