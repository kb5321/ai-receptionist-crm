from fastapi import FastAPI, HTTPException,Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
#from ringcentral_sms import send_sms

from config import DATABASE_URL, OPENAI_API_KEY
from auth import (
    require_login,
    require_admin,
    require_role,
    get_admin_role
)

from pydantic import BaseModel
from openai import OpenAI
from passlib.hash import pbkdf2_sha256
import re
import os

from database import get_db_connection
from routers import users
from routers import clients
from routers import leads

from audit import save_audit_log
from services.lead_service import save_lead



app = FastAPI()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app.include_router(users.router)
app.include_router(clients.router)
app.include_router(leads.router)



BUSINESS_KNOWLEDGE = """
Business Name: Terra Spa

Business Type:
Terra Spa is a spa business offering massage, facials, nails, and waxing services.

Website:
www.TerraSpaSa.com

Current Status:
Terra Spa is currently relocating and is not open for appointments at this time.

Booking Policy:
Clients can join the waitlist and Terra Spa will contact them when appointments become available again.

Gift Certificates:
Gift certificates will be honored after reopening. Clients should provide their name, phone number, and gift certificate details.

Client Communication Style:
Be polite, calm, professional, and helpful. Keep answers short and clear.

Important Rules:
- Do not invent prices.
- Do not invent appointment availability.
- Do not provide medical advice.
- If important booking information is missing, ask for the client's name, phone number, preferred service, and preferred time.
- If the client already provided booking details, confirm the request was added to the waitlist.
- If the client wants to book, explain that Terra Spa is relocating and can add them to the waitlist.
"""


class AskRequest(BaseModel):
    session_id: str
    question: str


def save_message(role, content, session_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO chat_messages (role, content, session_id)
        VALUES (%s, %s, %s)
        """,
        (role, content, session_id)
    )

    conn.commit()
    cur.close()
    conn.close()


def load_recent_messages(session_id, limit=10):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, content
        FROM chat_messages
        WHERE session_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (session_id, limit)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    rows.reverse()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]

# def save_lead(session_id, client_name, phone, service, preferred_time):
#     conn = get_db_connection()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         INSERT INTO spa_leads
#         (session_id, client_name, phone, service, preferred_time)
#         VALUES (%s, %s, %s, %s, %s)
#         """,
#         (session_id, client_name, phone, service, preferred_time)
#     )

#     conn.commit()
#     cur.close()
#     conn.close()



def update_client_from_appointment(appointment_id):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            client_name,
            phone,
            service
        FROM appointments
        WHERE id = %s
        """,
        (appointment_id,)
    )

    appointment = cur.fetchone()

    if appointment is None:
        cur.close()
        conn.close()
        return False

    client_name = appointment[0]
    phone = appointment[1]
    service = appointment[2]

    cur.execute(
        """
        SELECT id, total_visits
        FROM clients
        WHERE phone = %s
        """,
        (phone,)
    )

    existing_client = cur.fetchone()

    if existing_client:

        client_id = existing_client[0]
        visits = existing_client[1] + 1

        cur.execute(
            """
            UPDATE clients
            SET
                total_visits = %s,
                last_service = %s,
                last_appointment_date = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (visits, service, client_id)
        )

    else:

        cur.execute(
            """
            INSERT INTO clients
            (
                client_name,
                phone,
                total_visits,
                last_service,
                last_appointment_date
            )
            VALUES
            (
                %s,
                %s,
                1,
                %s,
                CURRENT_TIMESTAMP
            )
            """,
            (
                client_name,
                phone,
                service
            )
        )

    conn.commit()

    cur.close()
    conn.close()

    return True

def extract_lead_info(question):
    text = question.lower()

    services = ["massage", "facial", "waxing", "nails"]
    service = "Unknown"

    for s in services:
        if s in text:
            service = s
            break

    phone_match = re.search(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", question)
    phone = phone_match.group(0) if phone_match else "Unknown"

    preferred_time = "Unknown"
    time_keywords = ["today", "tomorrow", "morning", "afternoon", "evening", "friday", "saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"]

    for word in time_keywords:
        if word in text:
            preferred_time = word
            break

    client_name = "Unknown"

    name_match = re.search(r"my name is ([A-Za-z\s]+)", question, re.IGNORECASE)
    if name_match:
        client_name = name_match.group(1).strip()

    return client_name, phone, service, preferred_time

def create_sms_message(phone, message, source):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO sms_messages
        (phone, message, source)
        VALUES (%s, %s, %s)
        """,
        (phone, message, source)
    )

    conn.commit()
    cur.close()
    conn.close()

    return True



@app.get("/admin/audit-log", response_class=HTMLResponse)
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




@app.get("/")
def root():
    return {"message": "Hello AI Infrastructure World"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database_configured": DATABASE_URL is not None,
        "openai_configured": OPENAI_API_KEY is not None
    }


@app.get("/messages")
def get_messages():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, session_id, role, content, created_at
        FROM chat_messages
        ORDER BY created_at DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    messages = []

    for row in rows:
        messages.append({
            "id": row[0],
            "session_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": str(row[4])
        })

    return {
        "total_messages": len(messages),
        "messages": messages
    }

@app.get("/messages/{session_id}")
def get_messages_by_session(session_id: str):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, session_id, role, content, created_at
        FROM chat_messages
        WHERE session_id = %s
        ORDER BY created_at ASC
        """,
        (session_id,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    messages = []

    for row in rows:
        messages.append({
            "id": row[0],
            "session_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": str(row[4])
        })

    return {
        "session_id": session_id,
        "total_messages": len(messages),
        "messages": messages
    }

@app.get("/sessions")
def get_sessions():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            session_id,
            COUNT(*) AS message_count,
            MAX(created_at) AS last_message_at
        FROM chat_messages
        WHERE session_id IS NOT NULL
        GROUP BY session_id
        ORDER BY last_message_at DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    sessions = []

    for row in rows:
        sessions.append({
            "session_id": row[0],
            "message_count": row[1],
            "last_message_at": str(row[2])
        })

    return {
        "total_sessions": len(sessions),
        "sessions": sessions
    }

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM chat_messages
        WHERE session_id = %s
        """,
        (session_id,)
    )

    deleted_count = cur.rowcount

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "Session deleted successfully",
        "session_id": session_id,
        "deleted_messages": deleted_count
    }

@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Chat</title>

        <style>
            body {
                font-family: Arial;
                margin: 40px;
            }

            #chatBox {
                border: 1px solid #ccc;
                height: 400px;
                overflow-y: scroll;
                padding: 10px;
                margin-bottom: 20px;
            }

            .user {
                color: blue;
                margin-bottom: 10px;
            }

            .assistant {
                color: green;
                margin-bottom: 20px;
            }

            textarea {
                width: 100%;
            }
        </style>
    </head>

    <body>

        <h2>Terra Spa AI Chat</h2>

        <label>Session ID:</label>
        <input id="sessionId" value="test-001" />

        <br><br>

        <div id="chatBox"></div>

        <textarea
            id="question"
            rows="4"
            placeholder="Ask a question..."
            onkeydown="handleKey(event)"
        ></textarea>

        <p id="status"></p>

        <br><br>

        <button onclick="askAI()">Send</button>

        <script>

            async function loadMessages() {

                const sessionId =
                    document.getElementById("sessionId").value;

                const response =
                    await fetch(`/messages/${sessionId}`);

                const data = await response.json();

                const chatBox =
                    document.getElementById("chatBox");

                chatBox.innerHTML = "";

                data.messages.forEach(msg => {

                    const div = document.createElement("div");

                    div.className = msg.role;

                    div.innerHTML =
                        "<b>" + msg.role + ":</b> " + msg.content;

                    chatBox.appendChild(div);
                });

                chatBox.scrollTop = chatBox.scrollHeight;
            }

            function handleKey(event) {

                if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    askAI();
                }
            }


            async function askAI() {

                const sessionId =
                    document.getElementById("sessionId").value;

                const question =
                    document.getElementById("question").value;
                    document.getElementById("status").textContent = "AI is typing...";

                await fetch("/ask", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        question: question
                    })
                });

                document.getElementById("question").value = "";

                loadMessages();
            }

            loadMessages();
            document.getElementById("status").textContent = "";

        </script>

    </body>
    </html>
    """


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):

    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    return """
    <!DOCTYPE html>

<html>
<head>
    <title>Terra Spa Admin</title>


<style>
    body {
        font-family: Arial;
        margin: 40px;
    }

    .top-nav {
        margin-bottom: 25px;
    }

    .top-nav a {
        text-decoration: none;
        margin-right: 20px;
        font-size: 16px;
        font-weight: bold;
    }

    .menu {
        margin-top: 30px;
        width: 350px;
    }

    .menu a {
        display: block;
        padding: 12px;
        margin-bottom: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        text-decoration: none;
        font-size: 18px;
    }

    .menu a:hover {
        background-color: #f2f2f2;
    }
</style>


</head>

<body>


<div class="top-nav">
    <a href="/admin">🏠 Admin Home</a>
    <a href="/admin/logout">🚪 Logout</a>
</div>

<h2>Terra Spa Admin Dashboard</h2>

<div class="menu">
    <a href="/admin/leads">📋 Lead Dashboard</a>
    <a href="/admin/appointments">📅 Appointment Dashboard</a>
    <a href="/admin/clients">👤 Client Dashboard</a>
    <a href="/admin/sms">📱 SMS Dashboard</a>
    <a href="/admin/users">🔐 User Management</a>
    <a href="/admin/audit-log">🧾 Audit Log</a>
</div>


</body>
</html>

    """

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terra Spa Admin Login</title>

        <style>
            body {
                font-family: Arial;
                margin: 50px;
            }

            form {
                width: 300px;
            }

            input {
                width: 100%;
                padding: 8px;
                margin-top: 10px;
            }

            button {
                margin-top: 10px;
                padding: 8px 15px;
            }
        </style>
    </head>

    <body>

        <h2>Terra Spa Admin Login</h2>

        <form method="post" action="/admin/login">

            <input
                type="text"
                name="username"
                placeholder="Username"
                required
            >

            <input
                type="password"
                name="password"
                placeholder="Password"
                required
            >

            <button type="submit">
                Login
            </button>

        </form>

    </body>
    </html>
    """

@app.get("/admin/logout")
def admin_logout():

    response = RedirectResponse(
        url="/admin/login",
        status_code=302
    )

    response.delete_cookie("admin_logged_in")

    return response





@app.post("/admin/login")
def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT username,
               password_hash,
               role,
               is_active
        FROM admin_users
        WHERE username = %s
        """,
        (username,)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if user is None:

        return HTMLResponse(
            content="<h3>Invalid login. <a href='/admin/login'>Try again</a></h3>",
            status_code=401
        )

    db_username = user[0]
    password_hash = user[1]
    role = user[2]
    is_active = user[3]

    if not is_active:

        return HTMLResponse(
            content="<h3>Account disabled.</h3>",
            status_code=403
        )

    if not pbkdf2_sha256.verify(password, password_hash):

        return HTMLResponse(
            content="<h3>Invalid login. <a href='/admin/login'>Try again</a></h3>",
            status_code=401
        )

    response = RedirectResponse(
        url="/admin",
        status_code=302
    )

    response.set_cookie(
        key="admin_logged_in",
        value="true",
        httponly=True,
        samesite="lax"
    )

    response.set_cookie(
        key="admin_username",
        value=db_username,
        httponly=True,
        samesite="lax"
    )

    response.set_cookie(
        key="admin_role",
        value=role,
        httponly=True,
        samesite="lax"
    )

    save_audit_log(
        request,
        "LOGIN",
        f"User {db_username} logged in",
        username_override=db_username
    )

    return response


@app.get("/appointments")
def get_appointments():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
        id,
        lead_id,
        client_name,
        phone,
        service,
        appointment_time,
        status,
        created_at
        FROM appointments
        ORDER BY created_at DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    appointments = []

    for row in rows:
        appointments.append({
            "id": row[0],
            "lead_id": row[1],
            "client_name": row[2],
            "phone": row[3],
            "service": row[4],
            "appointment_time": row[5],
             "status": row[6],
            "created_at": str(row[7])
        })

    return {
        "total_appointments": len(appointments),
        "appointments": appointments
    }

@app.get("/admin/appointments", response_class=HTMLResponse)
def leads_admin_page(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terra Spa Appointments</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <div style="margin-bottom:20px;">
            <a href="/admin">🏠 Admin Home</a>
            &nbsp;&nbsp;&nbsp;
            <a href="/admin/logout">Logout</a>
        </div>
        <h2>Terra Spa Appointments</h2>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Lead ID</th>
                    <th>Client Name</th>
                    <th>Phone</th>
                    <th>Service</th>
                    <th>Appointment Time</th>
                    <th>Status</th>
                    <th>Created At</th>
                </tr>
            </thead>
            <tbody id="appointmentsTable"></tbody>
        </table>

        <script>
            async function loadAppointments() {
                const response = await fetch("/appointments");
                const data = await response.json();

                const table = document.getElementById("appointmentsTable");
                table.innerHTML = "";

                data.appointments.forEach(appt => {
                    const row = document.createElement("tr");

                    row.innerHTML = `
                        <td>${appt.id}</td>
                        <td>${appt.lead_id}</td>
                        <td>${appt.client_name}</td>
                        <td>${appt.phone}</td>
                        <td>${appt.service}</td>
                        <td>${appt.appointment_time}</td>

                        <td>
                            <select onchange="updateAppointmentStatus(${appt.id}, this.value)">
                                <option value="scheduled" ${appt.status === "scheduled" ? "selected" : ""}>scheduled</option>
                                <option value="confirmed" ${appt.status === "confirmed" ? "selected" : ""}>confirmed</option>
                                <option value="checked_in" ${appt.status === "checked_in" ? "selected" : ""}>checked_in</option>
                                <option value="completed" ${appt.status === "completed" ? "selected" : ""}>completed</option>
                                <option value="cancelled" ${appt.status === "cancelled" ? "selected" : ""}>cancelled</option>
                                <option value="no_show" ${appt.status === "no_show" ? "selected" : ""}>no_show</option>
                            </select>
                        </td>


                        <td>${appt.created_at}</td>
                    `;

                    table.appendChild(row);
                });
            }

            loadAppointments();
            async function updateAppointmentStatus(appointmentId, status) {

                await fetch(
                    `/appointments/${appointmentId}/status?status=${status}`,
                    {
                        method: "PUT"
                    }
                );

                loadAppointments();
            }

        </script>
    </body>
    </html>
    """

@app.put("/appointments/{appointment_id}/status")
def update_appointment_status(appointment_id: int, status: str):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE appointments
        SET status = %s
        WHERE id = %s
        """,
        (status, appointment_id)
    )

    updated_count = cur.rowcount

    conn.commit()

    client_updated = False

    if status == "completed":
        client_updated = update_client_from_appointment(
            appointment_id
        )

    sms_created = False

    if status == "confirmed":
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT client_name, phone, service, appointment_time
            FROM appointments
            WHERE id = %s
            """,
            (appointment_id,)
        )

        appointment = cur.fetchone()

        cur.close()
        conn.close()

        if appointment:
            client_name = appointment[0]
            phone = appointment[1]
            service = appointment[2]
            appointment_time = appointment[3]

            message = (
                f"Hi {client_name}, your Terra Spa {service} appointment "
                f"request for {appointment_time} has been confirmed."
            )

            create_sms_message(
                phone,
                message,
                "appointment_confirmed"
            )

            sms_created = True


    return {
        "message": "Appointment status updated",
        "appointment_id": appointment_id,
        "new_status": status,
        "updated_count": updated_count,
        "client_updated": client_updated,
        "sms_created": sms_created
    }

@app.get("/clients")
def get_clients(search: str = ""):

    conn = get_db_connection()
    cur = conn.cursor()

    if search:
        cur.execute(
            """
            SELECT id, client_name, phone, email, total_visits, last_service, last_appointment_date, created_at
            FROM clients
            WHERE client_name ILIKE %s
            OR phone ILIKE %s
            ORDER BY created_at DESC
            """,
            (f"%{search}%", f"%{search}%")
        )
    else:
        cur.execute(
            """
            SELECT id, client_name, phone, email, total_visits, last_service, last_appointment_date, created_at
            FROM clients
            ORDER BY created_at DESC
            """
        )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    clients = []

    for row in rows:
        clients.append({
            "id": row[0],
            "client_name": row[1],
            "phone": row[2],
            "email": row[3],
            "total_visits": row[4],
            "last_service": row[5],
            "last_appointment_date": str(row[6]),
            "created_at": str(row[7])
        })

    return {
        "total_clients": len(clients),
        "clients": clients
    }



@app.get("/sms")
def get_sms_messages():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            phone,
            message,
            status,
            source,
            created_at
        FROM sms_messages
        ORDER BY created_at DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    sms_messages = []

    for row in rows:
        sms_messages.append({
            "id": row[0],
            "phone": row[1],
            "message": row[2],
            "status": row[3],
            "source": row[4],
            "created_at": str(row[5])
        })

    return {
        "total_sms_messages": len(sms_messages),
        "sms_messages": sms_messages
    }

@app.get("/admin/sms", response_class=HTMLResponse)
def sms_admin_page(request: Request):

    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terra Spa SMS Queue</title>

        <style>
            body { font-family: Arial; margin: 40px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>

    <body>

        <div style="margin-bottom:20px;">
            <a href="/admin">🏠 Admin Home</a>
            &nbsp;&nbsp;&nbsp;
            <a href="/admin/logout">Logout</a>
        </div>

       

        <h2>Terra Spa SMS Queue</h2>
        <div id="smsStats" style="margin-bottom:20px; font-weight:bold;"></div>
        <button onclick="sendPendingSms()">
            Send All Pending SMS
        </button>
        <br><br>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Phone</th>
                    <th>Message</th>
                    <th>Status</th>
                    <th>Source</th>
                    <th>Created At</th>
                    <th>Action</th>
                </tr>
            </thead>

            <tbody id="smsTable"></tbody>
        </table>

        <script>
            async function loadSmsMessages() {
                const response = await fetch("/sms");
                const data = await response.json();

                const table = document.getElementById("smsTable");
                table.innerHTML = "";

                data.sms_messages.forEach(sms => {
                    const row = document.createElement("tr");

                    row.innerHTML = `
                        <td>${sms.id}</td>
                        <td>${sms.phone}</td>
                        <td>${sms.message}</td>
                        <td>
                            <select onchange="updateSmsStatus(${sms.id}, this.value)">
                                <option value="pending" ${sms.status === "pending" ? "selected" : ""}>pending</option>
                                <option value="sent" ${sms.status === "sent" ? "selected" : ""}>sent</option>
                                <option value="failed" ${sms.status === "failed" ? "selected" : ""}>failed</option>
                                <option value="cancelled" ${sms.status === "cancelled" ? "selected" : ""}>cancelled</option>
                            </select>
                        </td>


                        <td>${sms.source}</td>
                        <td>${sms.created_at}</td>
                        <td>
                            <button onclick="markSmsSent(${sms.id})">
                                Mark Sent
                            </button>
                        </td>
                    `;

                    table.appendChild(row);
                });
            }

            loadSmsStats();
            loadSmsMessages();

            async function updateSmsStatus(smsId, status) {
                await fetch(`/sms/${smsId}/status?status=${status}`, {
                    method: "PUT"
                });

                loadSmsMessages();
                loadSmsStats() 
            }

            async function markSmsSent(smsId) {
                await fetch(`/sms/${smsId}/status?status=sent`, {
                    method: "PUT"
                });

                loadSmsMessages();
                loadSmsStats() 
                
            }

            async function loadSmsStats() {
                const response = await fetch("/sms/stats");
                const stats = await response.json();

                document.getElementById("smsStats").innerHTML =
                    `Pending: ${stats.pending} |
                    Sent: ${stats.sent} |
                    Failed: ${stats.failed} |
                    Cancelled: ${stats.cancelled}`;
            }

            async function sendPendingSms() {
                await fetch("/sms/send-pending", {
                    method: "POST"
                });

                loadSmsStats();
                loadSmsMessages();
            }
        </script>

    </body>
    </html>
    """

@app.put("/sms/{sms_id}/status")
def update_sms_status(sms_id: int, status: str):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE sms_messages
        SET status = %s
        WHERE id = %s
        """,
        (status, sms_id)
    )

    updated_count = cur.rowcount

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "SMS status updated",
        "sms_id": sms_id,
        "new_status": status,
        "updated_count": updated_count
    }

@app.get("/sms/stats")
def get_sms_stats():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            status,
            COUNT(*)
        FROM sms_messages
        GROUP BY status
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    stats = {
        "pending": 0,
        "sent": 0,
        "failed": 0,
        "cancelled": 0
    }

    for row in rows:
        stats[row[0]] = row[1]

    return stats



@app.post("/sms/send-pending")
def send_pending_sms():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE sms_messages
        SET status = 'sent'
        WHERE status = 'pending'
        """
    )

    sent_count = cur.rowcount

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "Pending SMS messages marked as sent",
        "sent_count": sent_count
    }

@app.delete("/client-notes/{note_id}")
def delete_client_note(note_id: int):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM client_notes
        WHERE id = %s
        """,
        (note_id,)
    )

    deleted_count = cur.rowcount

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "Note deleted",
        "note_id": note_id,
        "deleted_count": deleted_count
    }


@app.get("/sms-messages/{message_id}")
def get_sms_message(message_id: int):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id,
               phone,
               message,
               status,
               created_at
        FROM sms_messages
        WHERE id = %s
        """,
        (message_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row is None:
        return {"error": "Message not found"}

    return {
        "id": row[0],
        "phone": row[1],
        "message": row[2],
        "status": row[3],
        "created_at": str(row[4])
    }

@app.post("/ask")
def ask_ai(request: AskRequest):
    try:
        previous_messages = load_recent_messages(request.session_id)

        messages = [
            {
                "role": "system",
                "content": f"""
                You are a professional AI receptionist for Terra Spa.

                Use the following business knowledge when answering clients:

                {BUSINESS_KNOWLEDGE}
                """
            }
        ]

        messages.extend(previous_messages)

        messages.append(
            {
                "role": "user",
                "content": request.question
            }
        )

        save_message(
            "user",
            request.question,
            request.session_id
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4
        )

        ai_answer = response.choices[0].message.content

        booking_keywords = [
            "book",
            "appointment",
            "schedule",
            "waitlist",
            "facial",
            "massage",
            "waxing",
            "nails"
        ]

        lead_saved = False

        if any(word in request.question.lower() for word in booking_keywords):
            client_name, phone, service, preferred_time = extract_lead_info(request.question)

            save_lead(
                request.session_id,
                client_name,
                phone,
                service,
                preferred_time
            )


            lead_saved = True

        save_message(
            "assistant",
            ai_answer,
            request.session_id
        )

        return {
            "session_id": request.session_id,
            "question": request.question,
            "answer": ai_answer,
            "messages_used_from_database": len(previous_messages),
            "lead_saved": lead_saved
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
    