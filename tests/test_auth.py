import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from main import app

client = TestClient(app)


def test_admin_clients_requires_login():
    response = client.get(
        "/admin/clients",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"

def test_admin_leads_requires_login():

    response = client.get(
        "/admin/leads",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"


def test_admin_appointments_requires_login():

    response = client.get(
        "/admin/appointments",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"


def test_admin_sms_requires_login():

    response = client.get(
        "/admin/sms",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"