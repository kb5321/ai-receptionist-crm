import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from services.appointment_service import (
    update_appointment_status_service
)


@pytest.fixture
def mock_db():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur
    mock_cur.rowcount = 1

    return mock_conn, mock_cur


def test_update_appointment_status_checked_in_no_sms(mock_db):
    """
    Purpose:
        Verify that changing an appointment status to
        'checked_in' does not trigger SMS sending or
        client updates.

    Scenario:
        An appointment arrives and is marked as
        checked_in.

    Expected Result:
        1. Appointment status is updated.
        2. No SMS is sent.
        3. No SMS record is created.
        4. No client update occurs.
        5. Function returns the expected values.

    What We Are Testing:
        Business logic inside
        update_appointment_status_service().

    Why This Matters:
        We previously discovered a bug where
        'checked_in' caused:

            UnboundLocalError: sms_sent

        This test permanently protects against
        that bug returning in future refactoring.

    Test Type:
        Unit Test
        Service Test
        Regression Test

    Mocking Strategy:
        Real database connections are replaced
        with fake objects (MagicMock).

        Real SMS sending is disabled.

        Real client updates are disabled.

        This allows us to test business logic
        without touching production systems.
    """

    mock_conn, mock_cur = mock_db

    with patch(
        "services.appointment_service.get_db_connection",
        return_value=mock_conn
    ), patch(
        "services.appointment_service.send_sms"
    ) as mock_send_sms, patch(
        "services.appointment_service.update_client_from_appointment"
    ) as mock_update_client:

        result = update_appointment_status_service(
            appointment_id=3,
            status="checked_in"
        )

        assert result["new_status"] == "checked_in"

        assert result["updated_count"] == 1

        assert result["client_updated"] is False

        assert result["sms_created"] is False

        assert result["sms_sent"] is False

        mock_send_sms.assert_not_called()

        mock_update_client.assert_not_called()

        

@pytest.mark.parametrize(
    "status",
    [
        "scheduled",
        "checked_in",
        "cancelled",
        "no_show"
    ]
)

def test_non_confirmed_status_does_not_send_sms(mock_db, status):
    """
    Purpose:
        Verify that statuses other than 'confirmed'
        do not send SMS messages.

    Business Rule:
        Only confirmed appointments send SMS.

    Test Type:
        Parameterized Unit Test
        Service Test
        Business Rule Test
    """

    mock_conn, mock_cur = mock_db

    with patch(
        "services.appointment_service.get_db_connection",
        return_value=mock_conn
    ), patch(
        "services.appointment_service.send_sms"
    ) as mock_send_sms, patch(
        "services.appointment_service.update_client_from_appointment"
    ) as mock_update_client:

        result = update_appointment_status_service(
            appointment_id=3,
            status=status
        )

        assert result["new_status"] == status
        assert result["sms_created"] is False
        assert result["sms_sent"] is False

        mock_send_sms.assert_not_called()



def test_completed_status_updates_client(mock_db):
    """
    Purpose:
        Verify that completed appointments update
        the client record.

    Business Rule:
        completed → update client

    Expected Result:
        update_client_from_appointment()
        is called exactly once.

    Test Type:
        Unit Test
        Service Test
        Business Rule Test
    """

    mock_conn, mock_cur = mock_db

    with patch(
        "services.appointment_service.get_db_connection",
        return_value=mock_conn
    ), patch(
        "services.appointment_service.update_client_from_appointment",
        return_value=True
    ) as mock_update_client:

        result = update_appointment_status_service(
            appointment_id=3,
            status="completed"
        )

        assert result["client_updated"] is True

        mock_update_client.assert_called_once_with(3)

def test_confirmed_status_sends_sms(mock_db):
    """
    Purpose:
        Verify that confirmed appointments
        send and log an SMS.

    Business Rule:
        confirmed → send SMS

    Expected Result:
        send_sms() is called
        save_sms_message() is called
        sms_sent=True
        sms_created=True

    Test Type:
        Unit Test
        Service Test
        Business Rule Test
    """

    mock_conn, mock_cur = mock_db

    mock_cur.fetchone.return_value = (
        "Tony",
        "2105551212",
        "Massage",
        "2026-06-08 10:00 AM"
    )

    with patch(
        "services.appointment_service.get_db_connection",
        return_value=mock_conn
    ), patch(
        "services.appointment_service.send_sms",
        return_value={
            "messageStatus": "Queued",
            "id": "12345"
        }
    ) as mock_send_sms, patch(
        "services.appointment_service.save_sms_message"
    ) as mock_save_sms:

        result = update_appointment_status_service(
            appointment_id=3,
            status="confirmed"
        )

        assert result["sms_sent"] is True
        assert result["sms_created"] is True

        mock_send_sms.assert_called_once()

        mock_save_sms.assert_called_once()