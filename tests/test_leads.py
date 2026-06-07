import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from main import app

client = TestClient(app)

def test_get_clients():

    response = client.get("/leads")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list) or "leads" in data