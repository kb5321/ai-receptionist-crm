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

def test_clients_router_health_check():
    response = client.get("/test-clients")

    assert response.status_code == 200
    assert response.json()["status"] == "clients router working" 


from unittest.mock import MagicMock, patch
#-----------------------------------------
# What This Test Is Proving
# Fake database result
# mock_cur.fetchall.return_value = [...]
# means:
# Do not fetch real clients.

# Pretend PostgreSQL returned:
# Tony
# Sarah

# Endpoint call
# response = client.get("/clients/top")
# means: Run FastAPI route

# JSON validation: assert data["top_clients"][0]["client_name"] == "Tony"

# proves:
# Tuple from database
# ↓
# Converted correctly
# ↓
# Returned as JSON

# Test Name:def test_get_top_clients_returns_top_five_clients():
# Scenario:
#     get top clients

# Expected:
#     returns top clients






#-------------------------------------------

def test_get_top_clients_returns_top_five_clients():

    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    mock_cur.fetchall.return_value = [
        (
            1,
            "Tony",
            "2105551111",
            12,
            "Massage"
        ),
        (
            2,
            "Sarah",
            "2105552222",
            10,
            "Facial"
        )
    ]

    with patch(
        "routers.clients.get_db_connection",
        return_value=mock_conn
    ):

        response = client.get("/clients/top")

        assert response.status_code == 200

        data = response.json()

        assert len(data["top_clients"]) == 2

        assert data["top_clients"][0]["client_name"] == "Tony"

        assert data["top_clients"][0]["total_visits"] == 12

        assert data["top_clients"][1]["client_name"] == "Sarah"

        assert data["top_clients"][1]["last_service"] == "Facial"

        mock_cur.execute.assert_called_once()

        mock_cur.close.assert_called_once()

        mock_conn.close.assert_called_once()

#----------------------------------------------------------
# What This Test Proves
# Arrange
# mock_cur.fetchone.return_value = (
#     25,
#     120,
#     4.8
# )

# Translation:
# Do not query PostgreSQL.

# Pretend the database returned:

# COUNT(*) = 25
# SUM(total_visits) = 120
# AVG(total_visits) = 4.8

# Act
# response = client.get("/clients/stats")
# Translation: Run FastAPI route

# Assert:assert data["total_clients"] == 25
# Proves:
# Database result
# ↓
# Mapped correctly
# ↓
# Returned in JSON

# Why This Is a Good Unit Test
# Your are testing:Route logic
# JSON transformation
# Business output

# You are not testing:
# PostgreSQL
# Network
# FastAPI internals
# because those are outside the scope of this function.

# Naming Review
# def test_get_client_stats_returns_summary_statistics():
#     A senior engineer immediately understands:
#     Function:
#     get_client_stats()

# Expected:
#     returns summary statistics
# without opening the test body.


#---------------------------------------------------------

def test_get_client_stats_returns_summary_statistics():

    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    mock_cur.fetchone.return_value = (
        25,     # total_clients
        120,    # total_visits
        4.8     # average_visits
    )

    with patch(
        "routers.clients.get_db_connection",
        return_value=mock_conn
    ):

        response = client.get("/clients/stats")

        assert response.status_code == 200

        data = response.json()

        assert data["total_clients"] == 25

        assert data["total_visits"] == 120

        assert data["average_visits"] == 4.8

        mock_cur.execute.assert_called_once()

        mock_cur.close.assert_called_once()

        mock_conn.close.assert_called_once()