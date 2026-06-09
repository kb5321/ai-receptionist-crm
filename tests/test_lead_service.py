import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from services.lead_service import (
    create_appointment_from_lead,
    save_lead,
)


def test_create_appointment_from_lead_returns_false_when_lead_missing():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = None

    with patch(
        "services.lead_service.get_db_connection",
        return_value=mock_conn
    ):
        result = create_appointment_from_lead(lead_id=99)

        assert result is False

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_create_appointment_from_lead_creates_appointment():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    mock_cur.fetchone.return_value = (
        5,
        "Tony",
        "+12105551212",
        "Massage",
        "2026-06-09 10:00 AM"
    )

    with patch(
        "services.lead_service.get_db_connection",
        return_value=mock_conn
    ):
        result = create_appointment_from_lead(lead_id=5)

        assert result is True

        assert mock_cur.execute.call_count == 2

        second_execute_args = mock_cur.execute.call_args_list[1][0]
        values = second_execute_args[1]

        assert values == (
            5,
            "Tony",
            "+12105551212",
            "Massage",
            "2026-06-09 10:00 AM"
        )

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_save_lead_inserts_lead_record():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    with patch(
        "services.lead_service.get_db_connection",
        return_value=mock_conn
    ):
        save_lead(
            session_id="session-123",
            client_name="Tony",
            phone="+12105551212",
            service="Facial",
            preferred_time="Tomorrow morning"
        )

        mock_cur.execute.assert_called_once()

        args = mock_cur.execute.call_args[0]
        values = args[1]

        assert values == (
            "session-123",
            "Tony",
            "+12105551212",
            "Facial",
            "Tomorrow morning"
        )

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()