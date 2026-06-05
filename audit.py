# audit.py

from fastapi import Request
from database import get_db_connection


def save_audit_log(
    request: Request,
    action: str,
    details: str = "",
    username_override: str = None
):
    username = username_override or request.cookies.get(
        "admin_username",
        "unknown"
    )

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO audit_log (username, action, details)
        VALUES (%s, %s, %s)
        """,
        (username, action, details)
    )

    conn.commit()
    cur.close()
    conn.close()