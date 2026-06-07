import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from main import app

client = TestClient(app)

def test_get_clients():
    response = client.get("/clients")

    assert response.status_code == 200

    data = response.json()

    assert "clients" in data

    assert isinstance(
        data["clients"],
        list
    )