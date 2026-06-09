import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from services.client_service import (
    create_client_note,
    update_client_from_appointment,
)


def test_create_client_note_inserts_note():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    with patch(
        "services.client_service.get_db_connection",
        return_value=mock_conn
    ):
        result = create_client_note(
            client_id=7,
            note="VIP client"
        )

        assert result is True

        mock_cur.execute.assert_called_once()

        args = mock_cur.execute.call_args[0]
        values = args[1]

        assert values == (
            7,
            "VIP client"
        )

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_update_client_from_appointment_returns_false_when_appointment_missing():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = None

    with patch(
        "services.client_service.get_db_connection",
        return_value=mock_conn
    ):
        result = update_client_from_appointment(
            appointment_id=99
        )

        assert result is False

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_update_client_from_appointment_updates_existing_client():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    mock_cur.fetchone.side_effect = [
        (
            "Tony",
            "+12105551212",
            "Massage"
        ),
        (
            4,
            2
        )
    ]

    with patch(
        "services.client_service.get_db_connection",
        return_value=mock_conn
    ):
        result = update_client_from_appointment(
            appointment_id=3
        )

        assert result is True

        assert mock_cur.execute.call_count == 3

        update_args = mock_cur.execute.call_args_list[2][0]
        values = update_args[1]

        assert values == (
            3,
            "Massage",
            4
        )

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_update_client_from_appointment_inserts_new_client():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    mock_cur.fetchone.side_effect = [
        (
            "Tony",
            "+12105551212",
            "Facial"
        ),
        None
    ]

    with patch(
        "services.client_service.get_db_connection",
        return_value=mock_conn
    ):
        result = update_client_from_appointment(
            appointment_id=3
        )

        assert result is True

        assert mock_cur.execute.call_count == 3

        insert_args = mock_cur.execute.call_args_list[2][0]
        values = insert_args[1]

        assert values == (
            "Tony",
            "+12105551212",
            "Facial"
        )

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()