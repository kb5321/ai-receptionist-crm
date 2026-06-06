# =====================================
# Client Pages
# =====================================

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from database import get_db_connection

from auth import require_admin, require_login

from services.client_service import create_client_note

from ringcentral_sms import send_sms
from services.sms_service import save_sms_message


router = APIRouter()

@router.get("/test-clients")
def test_clients():
    return {"status": "clients router working"}

# =====================================
# Client API Routes
# =====================================

@router.get("/clients")
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





# =====================================
# Client Dashboard / Reports
# =====================================

@router.get("/clients/top")
def get_top_clients():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            client_name,
            phone,
            total_visits,
            last_service
        FROM clients
        ORDER BY total_visits DESC
        LIMIT 5
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    top_clients = []

    for row in rows:
        top_clients.append({
            "id": row[0],
            "client_name": row[1],
            "phone": row[2],
            "total_visits": row[3],
            "last_service": row[4]
        })

    return {
        "top_clients": top_clients
    }


@router.get("/clients/stats")
def get_client_stats():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(total_visits), 0),
            COALESCE(AVG(total_visits), 0)
        FROM clients
        """
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "total_clients": row[0],
        "total_visits": row[1],
        "average_visits": round(float(row[2]), 2)
    }






# =====================================
# Client Admin Pages
# =====================================

@router.get("/admin/clients", response_class=HTMLResponse)
def leads_admin_page(request: Request):
    if not require_login(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302
        )
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terra Spa Clients</title>

        <style>
            body {
                font-family: Arial;
                margin: 40px;
            }

            table {
                border-collapse: collapse;
                width: 100%;
            }

            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }

            th {
                background-color: #f2f2f2;
            }

            h2 {
                margin-bottom: 20px;
            }
        </style>
    </head>

    <body>
        <div style="margin-bottom:20px;">
            <a href="/admin">🏠 Admin Home</a>
            &nbsp;&nbsp;&nbsp;
            <a href="/admin/logout">Logout</a>
        </div>
        <h2>Terra Spa Client Dashboard</h2>

        <div
            id="clientStats"
            style="
                margin-bottom:20px;
                font-weight:bold;
                padding:10px;
                border:1px solid #ccc;
            "
        >
        </div>

        <h3>Top Clients</h3>
        <div id="topClients"></div>



        <input
            id="clientSearch"
            type="text"
            placeholder="Search by name or phone"
            style="padding:8px; width:300px;"
            onkeydown="handleClientSearchKey(event)"
        >

        <button onclick="loadClients()">
            Search
        </button>
        <button onclick="clearClientSearch()">
            Clear
        </button>

        <br><br>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Client Name</th>
                    <th>Phone</th>
                    <th>Email</th>
                    <th>Total Visits</th>
                    <th>Last Service</th>
                    <th>Last Appointment</th>
                    <th>Created At</th>
                </tr>
            </thead>

            <tbody id="clientsTable">
            </tbody>

        </table>

        <script>

            async function loadClients() {

                const search =
                    document.getElementById("clientSearch").value;

                const response =
                    await fetch("/clients?search=" + encodeURIComponent(search));

                const data = await response.json();

                const table =
                    document.getElementById("clientsTable");

                table.innerHTML = "";

                data.clients.forEach(client => {

                    const row =
                        document.createElement("tr");

                    row.innerHTML = `
                        <td>${client.id}</td>
                        <td>
                            <a href="/admin/clients/${client.id}">
                                ${client.client_name}
                            </a>
                        </td>
                        <td>${client.phone}</td>
                        <td>${client.email || ""}</td>
                        <td>${client.total_visits}</td>
                        <td>${client.last_service || ""}</td>
                        <td>${client.last_appointment_date || ""}</td>
                        <td>${client.created_at}</td>
                    `;

                    table.appendChild(row);
                });
            }

            async function loadClientStats() {

                const response =
                    await fetch("/clients/stats");

                const stats =
                    await response.json();

                document.getElementById(
                    "clientStats"
                ).innerHTML =

                    `Total Clients: ${stats.total_clients}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    Total Visits: ${stats.total_visits}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    Average Visits: ${stats.average_visits}`;
            }

            loadClientStats()
            loadTopClients()
            loadClients();

            function handleClientSearchKey(event) {
                if (event.key === "Enter") {
                    loadClients();
                }
            }

            function clearClientSearch() {
                document.getElementById("clientSearch").value = "";
                loadClients();
            }

            async function loadTopClients() {
                const response = await fetch("/clients/top");
                const data = await response.json();

                let html = "<ul>";

                data.top_clients.forEach(client => {
                    html += `
                        <li>
                            <a href="/admin/clients/${client.id}">
                                ${client.client_name}
                            </a>
                            - ${client.total_visits} visits
                            - Last Service: ${client.last_service || ""}
                        </li>
                    `;
                });

                html += "</ul>";

                document.getElementById("topClients").innerHTML = html;
            }

        </script>

    </body>
    </html>
 
       """

@router.get("/admin/clients/{client_id}", response_class=HTMLResponse)
def client_profile_page(client_id: int, request: Request):

    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            client_name,
            phone,
            email,
            total_visits,
            last_service,
            last_appointment_date,
            created_at
        FROM clients
        WHERE id = %s
        """,
        (client_id,)
    )

    client = cur.fetchone()

    if client is None:
        cur.close()
        conn.close()
        return HTMLResponse(
            content="<h3>Client not found</h3>",
            status_code=404
        )

    cur.execute(
        """
        SELECT
            id,
            service,
            appointment_time,
            status,
            created_at
        FROM appointments
        WHERE phone = %s
        ORDER BY created_at DESC
        """,
        (client[2],)
    )

    appointment_rows = cur.fetchall()

    cur.execute(
        """
        SELECT DISTINCT session_id
        FROM spa_leads
        WHERE phone = %s
        """,
        (client[2],)
    )

    session_rows = cur.fetchall()

    session_ids = [row[0] for row in session_rows]

    conversation_rows = []

    if session_ids:
        cur.execute(
            """
            SELECT role, content, created_at
            FROM chat_messages
            WHERE session_id = ANY(%s)
            ORDER BY created_at ASC
            """,
            (session_ids,)
        )

        conversation_rows = cur.fetchall()
    
    cur.execute(
        """
        SELECT
            id,
            note,
            created_at
        FROM client_notes
        WHERE client_id = %s
        ORDER BY created_at DESC
        """,
        (client_id,)
    )

    note_rows = cur.fetchall()

    
    cur.execute(
        """
        SELECT
            id,
            created_at,
            status,
            direction

        FROM sms_messages
        WHERE client_id = %s
        ORDER BY created_at DESC
        """,
        (client_id,)
    )

    sms_rows = cur.fetchall()

    cur.close()
    conn.close()

    
    appointments_html = ""

    for appt in appointment_rows:

        appointments_html += f"""
            <tr>
                <td>{appt[0]}</td>
                <td>{appt[1]}</td>
                <td>{appt[2]}</td>
                <td>{appt[3]}</td>
                <td>{appt[4]}</td>
            </tr>
    """
    
    conversation_html = ""

    for msg in conversation_rows:
        conversation_html += f"""
            <tr>
                <td>{msg[0]}</td>
                <td>{msg[1]}</td>
                <td>{msg[2]}</td>
            </tr>
        """
    notes_html = ""

    for note in note_rows:
        notes_html += f"""
            <tr>
                <td>{note[0]}</td>
                <td>{note[1]}</td>
                <td>{note[2]}</td>
                <td>
                    <button onclick="deleteNote({note[0]})">
                        Delete
                    </button>
                </td>
            </tr>
        """

    sms_html = ""

    for sms in sms_rows:
        sms_html += f"""
            <tr>
                <td>{sms[1]}</td>
                <td>{sms[2]}</td>
                <td>{sms[3]}</td>
                <td>
                    <button onclick="viewMessage({sms[0]})">
                        View Message - ({sms[0]})
                    </button>
                </td>
            </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Client Profile</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}

            .card {{
                border: 1px solid #ccc;
                padding: 20px;
                width: 500px;
            }}

            a {{
                display: inline-block;
                margin-bottom: 20px;
            }}

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

            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.4);
            }}

            .modal-content {{
                background-color: white;
                margin: 10% auto;
                padding: 20px;
                border: 1px solid #ccc;
                width: 500px;
            }}

            .close {{
                float: right;
                font-size: 24px;
                cursor: pointer;
            }}

            .action-card {{
                border: 1px solid #ccc;
                padding: 20px;
                margin-top: 15px;
                margin-bottom: 20px;
                background-color: #f9f9f9;
                width: 600px;
            }}
        </style>
    </head>
    <body>

        <a href="/admin/clients">Back to Clients</a>
        <a href="/admin/logout" style="margin-left:20px;">Logout</a>

        <h2>Client Profile</h2>

        <div class="card">
            <p><strong>ID:</strong> {client[0]}</p>
            <p><strong>Name:</strong> {client[1]}</p>
            <p><strong>Phone:</strong> {client[2]}</p>
            <p><strong>Email:</strong> {client[3] or ""}</p>
            <p><strong>Total Visits:</strong> {client[4]}</p>
            <p><strong>Last Service:</strong> {client[5] or ""}</p>
            <p><strong>Last Appointment:</strong> {client[6]}</p>
            <p><strong>Created At:</strong> {client[7]}</p>
        </div>

        <h3>Quick Actions</h3>
     <div class="action-card">
        <h4>Send SMS</h4>

        <form method="post" action="/clients/{client_id}/send-sms">
            <input type="hidden" name="phone" value="{client[2]}">

            <label><strong>Template:</strong></label>

            <select id="smsTemplate" onchange="loadSmsTemplate()">
                <option value="">-- Select Template --</option>

                <option value="birthday">
                    Birthday Greeting
                </option>

                <option value="reminder">
                    Appointment Reminder
                </option>

                <option value="followup">
                    Follow-Up
                </option>

                <option value="thankyou">
                    Thank You
                </option>
            </select>

            <br><br>

           <textarea
                id="smsMessage"
                name="message"
                rows="4"
                cols="80"
                placeholder="Enter SMS message..."
                required
            ></textarea>

            <br><br>

            <button type="submit">Send SMS</button>
        </form>
        </div>
        <div class="action-card">
        <h4>Add Client Note</h4>

        <form method="post" action="/clients/{client_id}/notes">
            <textarea
                name="note"
                rows="4"
                cols="80"
                placeholder="Enter note..."
                required
            ></textarea>
            <br><br>
            <button type="submit">Save Note</button>
        </form>
        </div>

        



    <h3>SMS History</h3>

    <table>
        <thead>
            <tr>
                <th>Date / Time</th>
                <th>Status</th>
                <th>Direction</th>
                <th>Action</th>
            </tr>
        </thead>

        <tbody>
            {sms_html}
        </tbody>
    </table>

    <h3>Client Notes</h3>

    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Note</th>
                <th>Created At</th>
                <th>Action</th>
            </tr>
        </thead>

        <tbody>
            {notes_html}
        </tbody>
    </table>


    <h3>Appointment History</h3>

    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Service</th>
                <th>Appointment Time</th>
                <th>Status</th>
                <th>Created At</th>
            </tr>
        </thead>

        <tbody>
            {appointments_html}
        </tbody>

    </table>


    <h3>Conversation History</h3>

    <table>
        <thead>
            <tr>
                <th>Role</th>
                <th>Message</th>
                <th>Created At</th>
            </tr>
        </thead>

        <tbody>
            {conversation_html}
        </tbody>
    </table>

    <script>
        async function deleteNote(noteId) {{

            await fetch(
                "/client-notes/" + noteId,
                {{
                    method: "DELETE"
                }}
            );

            location.reload();
        }}

        async function viewMessage(messageId) {{
            const response = await fetch("/sms-messages/" + messageId);
            const data = await response.json();

            document.getElementById("modalPhone").innerText = data.phone || "";
            document.getElementById("modalStatus").innerText = data.status || "";
            document.getElementById("modalCreatedAt").innerText = data.created_at || "";
            document.getElementById("modalMessage").innerText = data.message || "";

            document.getElementById("smsModal").style.display = "block";
        }}

        function closeSmsModal() {{
            document.getElementById("smsModal").style.display = "none";
        }}

        function loadSmsTemplate() {{

                const template =
                    document.getElementById("smsTemplate").value;

                const textarea =
                    document.getElementById("smsMessage");

                if (template === "birthday") {{

                    textarea.value =
                        "Happy Birthday! 🎉 Terra Spa wishes you a wonderful day. We look forward to seeing you soon.";

                }}

                else if (template === "reminder") {{

                    textarea.value =
                        "This is a friendly reminder from Terra Spa about your upcoming appointment. Please reply YES to confirm.";

                }}

                else if (template === "followup") {{

                    textarea.value =
                        "Thank you for visiting Terra Spa. We hope you enjoyed your service. We would love to see you again soon.";

                }}

                else if (template === "thankyou") {{

                    textarea.value =
                        "Thank you for choosing Terra Spa. We truly appreciate your business and look forward to serving you again.";

                }}

                else {{

                    textarea.value = "";

                }}
            }}

     </script>

        <div id="smsModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeSmsModal()">&times;</span>

            <h3>SMS Message</h3>

            <p><strong>Phone:</strong> <span id="modalPhone"></span></p>
            <p><strong>Status:</strong> <span id="modalStatus"></span></p>
            <p><strong>Created At:</strong> <span id="modalCreatedAt"></span></p>

            <hr>

            <p><strong>Message:</strong></p>
            <p id="modalMessage"></p>
        </div>
        </div>


</body>
    </html>
    """

# =====================================
# Client sms
# =====================================
@router.post("/clients/{client_id}/send-sms")
def send_client_sms(
    client_id: int,
    phone: str = Form(...),
    message: str = Form(...)
):
    result = send_sms(phone, message)

    save_sms_message(
        client_id=client_id,
        phone=phone,
        message=message,
        status=result.get("messageStatus"),
        ringcentral_message_id=result.get("id")
    )

    return RedirectResponse(
        url=f"/admin/clients/{client_id}",
        status_code=303
    )


# =====================================
# Client Notes
# =====================================
@router.post("/clients/{client_id}/notes")
def add_client_note(
        client_id: int,
        note: str = Form(...)
    ):

    create_client_note(
        client_id,
        note
    )

    return RedirectResponse(
        url=f"/admin/clients/{client_id}",
        status_code=302
    )

@router.delete("/client-notes/{note_id}")
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


