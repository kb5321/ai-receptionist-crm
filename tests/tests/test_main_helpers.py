import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from main import (
    save_message,
    load_recent_messages,
    extract_lead_info,
)


def test_extract_lead_info_finds_name_phone_service_and_time():
    question = (
        "Hi, my name is Tony Bati. "
        "I want to book a massage tomorrow. "
        "My phone is 210-555-1212."
    )

    client_name, phone, service, preferred_time = extract_lead_info(question)

    assert client_name == "Tony Bati"
    assert phone == "210-555-1212"
    assert service == "massage"
    assert preferred_time == "tomorrow"

def test_extract_lead_info_returns_unknown_when_missing():
    question = "Hello, I have a question."

    client_name, phone, service, preferred_time = extract_lead_info(question)

    assert client_name == "Unknown"
    assert phone == "Unknown"
    assert service == "Unknown"
    assert preferred_time == "Unknown"

def test_save_message_inserts_chat_message():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    with patch(
        "main.get_db_connection",
        return_value=mock_conn
    ):
        save_message(
            role="user",
            content="Hello",
            session_id="session-123"
        )

        mock_cur.execute.assert_called_once()

        args = mock_cur.execute.call_args[0]
        values = args[1]

        assert values == (
            "user",
            "Hello",
            "session-123"
        )

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

def test_load_recent_messages_returns_messages_in_original_order():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    mock_cur.fetchall.return_value = [
        ("assistant", "Second message"),
        ("user", "First message"),
    ]

    with patch(
        "main.get_db_connection",
        return_value=mock_conn
    ):
        result = load_recent_messages(
            session_id="session-123",
            limit=10
        )

        assert result == [
            {
                "role": "user",
                "content": "First message"
            },
            {
                "role": "assistant",
                "content": "Second message"
            }
        ]

        mock_cur.execute.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()