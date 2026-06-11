# =====================================
# Admin User Management Routes
# =====================================

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from database import get_db_connection
from auth import require_admin

from passlib.hash import pbkdf2_sha256
from audit import save_audit_log

router = APIRouter()

# 1. List users

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
    <h1> AI Receptionist CRM</h1>
    <!-- Navigation Bar -->
        <div class="navbar">
            <a href="/admin">🏠 Dashboard</a>
            <a href="/admin/leads">📋 Leads</a>
            <a href="/admin/appointments">📅 Appointments</a>
            <a href="/admin/clients">👥 Clients</a>
            <a href="/admin/sms">💬 Messages</a>
            <a href="/admin/users">🔐 Users</a>
            <a href="/admin/audit-log">📜 Audit Log</a>

            <span style="float:right">
                <a href="/admin/logout">Logout</a>
            </span>
        </div>

        <!-- Page Content -->
   
        <h2>User Management</h2>
        <p>Manage administrators, roles, and permissions</p>
       

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





# 2. Show new user form

@router.get("/admin/users/new", response_class=HTMLResponse)
def new_admin_user_page(request: Request):

    if not require_admin(request):
        return HTMLResponse("<h3>Access Denied</h3>", status_code=403)

    return """
    <h2>Create Admin User</h2>

    <form method="post" action="/admin/users/new">
        <label>Username</label><br>
        <input type="text" name="username" required><br><br>

        <label>Password</label><br>
        <input type="password" name="password" required><br><br>

        <label>Role</label><br>
        <select name="role">
            <option value="staff">staff</option>
            <option value="admin">admin</option>
            <option value="viewer">viewer</option>
       
        </select><br><br>

        <button type="submit">Create User</button>
    </form>

    <br>
    <a href="/admin/users">Back to Users</a>
    """


# 3. Create new user
@router.post("/admin/users/new")
def create_admin_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)
):

    if not require_admin(request):
        return HTMLResponse("<h3>Access Denied</h3>", status_code=403)

    password_hash = pbkdf2_sha256.hash(password)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO admin_users (username, password_hash, role)
        VALUES (%s, %s, %s)
        """,
        (username, password_hash, role)
    )

    conn.commit()
    save_audit_log(
        request,
        "CREATE_USER",
        f"Created user: {username} with role: {role}"
    )
    cur.close()
    conn.close()

    return RedirectResponse(
        url="/admin/users",
        status_code=303
    )


# 4. Toggle enable/disable
@router.post("/admin/users/{user_id}/toggle")
def toggle_admin_user(request: Request, user_id: int):
    if not require_admin(request):
        return HTMLResponse("<h3>Access Denied</h3>", status_code=403)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE admin_users
        SET is_active = NOT is_active
        WHERE id = %s
        """,
        (user_id,)
    )

    conn.commit()
    save_audit_log(
        request,
        "TOGGLE_USER",
        f"Toggled active status for user ID {user_id}"
    )
    cur.close()
    conn.close()

    return RedirectResponse(url="/admin/users", status_code=303)


# 5. Update role
@router.post("/admin/users/{user_id}/role")
def update_user_role(
    request: Request,
    user_id: int,
    role: str = Form(...)
):

    if not require_admin(request):
        return HTMLResponse(
            "<h3>Access Denied</h3>",
            status_code=403
        )
    
    if role not in ["admin", "staff", "viewer"]:
        return HTMLResponse(
        "<h3>Invalid role</h3>",
        status_code=400
    )

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE admin_users
        SET role = %s
        WHERE id = %s
        """,
        (
            role,
            user_id
        )
    )

    conn.commit()

    save_audit_log(
        request,
        "CHANGE_ROLE",
        f"Changed user ID {user_id} to role {role}"
    )

    cur.close()
    conn.close()

    return RedirectResponse(
        url="/admin/users",
        status_code=303
    )


# 6. Show reset password form
@router.get("/admin/users/{user_id}/reset-password", response_class=HTMLResponse)
def reset_password_page(
    request: Request,
    user_id: int
):

    if not require_admin(request):
        return HTMLResponse(
            "<h3>Access Denied</h3>",
            status_code=403
        )

    return f"""
    <h2>Reset Password</h2>

    <form method="post"
          action="/admin/users/{user_id}/reset-password">

        <label>New Password</label>
        <br>

        <input
            type="password"
            name="new_password"
            required
        >

        <br><br>

        <button type="submit">
            Update Password
        </button>

    </form>

    <br>

    <a href="/admin/users">
        Back to Users
    </a>
    """

# 7. Reset password
@router.post("/admin/users/{user_id}/reset-password")
def reset_password(
    request: Request,
    user_id: int,
    new_password: str = Form(...)
):

    if not require_admin(request):
        return HTMLResponse(
            "<h3>Access Denied</h3>",
            status_code=403
        )

    password_hash = pbkdf2_sha256.hash(
        new_password
    )

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE admin_users
        SET password_hash = %s
        WHERE id = %s
        """,
        (
            password_hash,
            user_id
        )
    )

    conn.commit()

    save_audit_log(
        request,
        "RESET_PASSWORD",
        f"Reset password for user ID {user_id}"
    )

    cur.close()
    conn.close()

    return RedirectResponse(
        url="/admin/users",
        status_code=303
    )

