import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from audit import save_audit_log


class MockRequest:
    def __init__(self, cookies):
        self.cookies = cookies


def test_save_audit_log_uses_cookie_username():
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.cursor.return_value = mock_cur

    request = MockRequest(
        {
            "admin_username": "tony"
        }
    )

    with patch(
        "audit.get_db_connection",
        return_value=mock_conn
    ):

        save_audit_log(
            request=request,
            action="LOGIN",
            details="User logged in"
        )

        mock_cur.execute.assert_called_once()

        args = mock_cur.execute.call_args[0]

        values = args[1]

        assert values == (
            "tony",
            "LOGIN",
            "User logged in"
        )

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()