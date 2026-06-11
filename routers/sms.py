from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db_connection
from auth import require_admin, require_login

router = APIRouter()

@router.get("/sms")
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

#---------------------------------------------
@router.get("/admin/sms", response_class=HTMLResponse)
def sms_admin_page(request: Request):

    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Receptionist CRM SMS Queue</title>

        <style>
            body { font-family: Arial; margin: 40px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
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
   
    <h2>SMS Message Center</h2>
    <p>Manage outbound and inbound communications</p>
        <!-- sms Table -->
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


#------------------------------------------------------------------------
@router.put("/sms/{sms_id}/status")
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
#------------------------------------------------------------

@router.get("/sms/stats")
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


#-------------------------------------------------------------------------

@router.post("/sms/send-pending")
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



#-------------------------------------------------------------------------

@router.get("/sms-messages/{message_id}")
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
