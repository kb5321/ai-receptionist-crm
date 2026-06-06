
from pydantic import BaseModel
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from database import get_db_connection
from auth import require_admin, require_login

router = APIRouter()

@router.get("/admin/audit-log", response_class=HTMLResponse)
def admin_audit_log_page(request: Request):

    if not require_admin(request):
        return HTMLResponse(
            "<h3>Access Denied</h3>",
            status_code=403
        )

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, username, action, details, created_at
        FROM audit_log
        ORDER BY created_at DESC
        LIMIT 100
        """
    )

    logs = cur.fetchall()

    cur.close()
    conn.close()

    logs_html = ""

    for log in logs:
        logs_html += f"""
        <tr>
            <td>{log[0]}</td>
            <td>{log[1]}</td>
            <td>{log[2]}</td>
            <td>{log[3]}</td>
            <td>{log[4]}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Audit Log</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}

            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
            }}

            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }}

            th {{
                background-color: #f2f2f2;
            }}

            a {{
                display: inline-block;
                margin-bottom: 20px;
            }}
        </style>
    </head>

    <body>

        <div style="margin-bottom:20px;">
            <a href="/admin">🏠 Admin Home</a>
            &nbsp;&nbsp;&nbsp;
            <a href="/admin/logout">Logout</a>
        </div>

        <h2>Audit Log</h2>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Action</th>
                    <th>Details</th>
                    <th>Created At</th>
                </tr>
            </thead>

            <tbody>
                {logs_html}
            </tbody>
        </table>

    </body>
    </html>
    """
