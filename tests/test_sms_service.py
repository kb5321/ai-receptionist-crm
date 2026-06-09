import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from services.sms_service import (
    save_sms_message,
    create_sms_message,
)


def test_save_sms_message_inserts_outbound_ringcentral_sms():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    with patch(
        "services.sms_service.get_db_connection",
        return_value=mock_conn
    ):
        save_sms_message(
            client_id=7,
            phone="+12105551212",
            message="Test message",
            status="Queued",
            ringcentral_message_id="abc123"
        )

        mock_cur.execute.assert_called_once()

        args = mock_cur.execute.call_args[0]
        values = args[1]

        assert values == (
            7,
            "+12105551212",
            "Test message",
            "Queued",
            "RingCentral",
            "Outbound",
            "abc123"
        )

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_create_sms_message_inserts_basic_sms_record():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    with patch(
        "services.sms_service.get_db_connection",
        return_value=mock_conn
    ):
        result = create_sms_message(
            phone="+12105551212",
            message="Pending confirmation",
            source="appointment_confirmed"
        )

        assert result is True

        mock_cur.execute.assert_called_once()

        args = mock_cur.execute.call_args[0]
        values = args[1]

        assert values == (
            "+12105551212",
            "Pending confirmation",
            "appointment_confirmed"
        )

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()