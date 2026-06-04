from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from database import get_db_connection
from auth import require_admin

router = APIRouter()


@router.get("/test-users-2")
def test_users():
    return {"status": "users router working-2"}

@router.get("/test-admin")
def users():
    return {"status": "Admin/test users router working"}


@router.get("/admin/users", response_class=HTMLResponse)
def admin_users_page(request: Request):

    if not require_admin(request):
        return HTMLResponse(
            "<h3>Access Denied</h3>",
            status_code=403
        )

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, username, role, is_active, created_at
        FROM admin_users
        ORDER BY id
        """
    )

    users = cur.fetchall()

    cur.close()
    conn.close()

    users_html = ""

    for user in users:
        active_text = "Yes" if user[3] else "No"

        users_html += f"""
        <tr>
            <td>{user[0]}</td>
            <td>{user[1]}</td>

            <td>
                <form method="post" action="/admin/users/{user[0]}/role">

                    <select name="role">
                        <option value="admin" {"selected" if user[2] == "admin" else ""}>
                            admin
                        </option>

                        <option value="staff" {"selected" if user[2] == "staff" else ""}>
                            staff
                        </option>

                        <option value="viewer" {"selected" if user[2] == "viewer" else ""}>
                            viewer
                        </option>
                    </select>

                    <button type="submit">
                        Update
                    </button>

                </form>
            </td>

            <td>{active_text}</td>
            <td>{user[4]}</td>

            <td>
                <form method="post" action="/admin/users/{user[0]}/toggle">
                    <button type="submit">
                        {'Disable' if user[3] else 'Enable'}
                    </button>
                </form>
            </td>

            <td>
                <a href="/admin/users/{user[0]}/reset-password">
                    Reset Password
                </a>
            </td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Users</title>
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

        <h2>Admin Users</h2>
       

        <a
            href="/admin/users/new"
            style="
                display:inline-block;
                padding:10px 15px;
                background:#4CAF50;
                color:white;
                text-decoration:none;
                margin-bottom:15px;
            "
        >
    ➕ Create New User
</a>




        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Role</th>
                    <th>Active</th>
                    <th>Created At</th>
                    <th>Action</th>
                    <th>Password</th>
                </tr>
            </thead>

            <tbody>
                {users_html}
            </tbody>
        </table>

    </body>
    </html>
    """
