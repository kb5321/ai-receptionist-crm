from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Request
from database import get_db_connection
from auth import require_admin, require_login
from services.lead_service import create_appointment_from_lead,save_lead
from pydantic import BaseModel

# =====================================
# Request Models
# =====================================
class LeadRequest(BaseModel):
    session_id: str
    client_name: str
    phone: str
    service: str
    preferred_time: str

# =====================================
# Router
# =====================================
router = APIRouter()




# =====================================
# Lead Dashboard
# =====================================

@router.get("/admin/leads", response_class=HTMLResponse)
def leads_admin_page(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Receptionist CRM Leads</title>

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
    <h2>Lead Management</h2>
    

        <p>
            Manage and track customer leads.
        </p>

        <!-- Leads Table -->
        

        
        

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Client Name</th>
                    <th>Phone</th>
                    <th>Service</th>
                    <th>Preferred Time</th>
                    <th>Session ID</th>
                    <th>Status</th>
                    <th>Created At</th>
                </tr>
            </thead>

            <tbody id="leadsTable">
            </tbody>
        </table>

        <script>
            async function loadLeads() {
                const response = await fetch("/leads");
                const data = await response.json();

                const table = document.getElementById("leadsTable");
                table.innerHTML = "";

                data.leads.forEach(lead => {
                    const row = document.createElement("tr");

                    row.innerHTML = `
                        <tr>
                            <td>${lead.id}</td>
                            <td>${lead.client_name}</td>
                            <td>${lead.phone}</td>
                            <td>${lead.service}</td>
                            <td>${lead.preferred_time}</td>
                            <td>${lead.session_id}</td>
                            <td>
                                <select onchange="updateStatus(${lead.id}, this.value)">
                                    <option value="new" ${lead.status === "new" ? "selected" : ""}>new</option>
                                    <option value="contacted" ${lead.status === "contacted" ? "selected" : ""}>contacted</option>
                                    <option value="booked" ${lead.status === "booked" ? "selected" : ""}>booked</option>
                                    <option value="closed" ${lead.status === "closed" ? "selected" : ""}>closed</option>
                                </select>
                            </td>
                            <td>${lead.created_at}</td>
                        </tr>
                    `;

                    table.appendChild(row);
                });
            }

            loadLeads();

            async function updateStatus(leadId, status) {
                await fetch(`/leads/${leadId}/status?status=${status}`, {
                    method: "PUT"
                });

                loadLeads();
            }
        </script>
    </body>
    </html>
    """


# =====================================
# Lead APIs
# =====================================
@router.put("/leads/{lead_id}/status")
def update_lead_status(lead_id: int, status: str):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE spa_leads
        SET status = %s
        WHERE id = %s
        """,
        (status, lead_id)
    )

    conn.commit()

    appointment_created = False

    if status == "booked":
        appointment_created = create_appointment_from_lead(lead_id)

        cur.close()
        conn.close()

    return {
        "message": "Lead status updated",
        "lead_id": lead_id,
        "new_status": status,
        "appointment_created": appointment_created
    }

@router.post("/leads")
def create_lead(request: LeadRequest):

    save_lead(
        request.session_id,
        request.client_name,
        request.phone,
        request.service,
        request.preferred_time
    )

    return {
        "message": "Lead saved successfully",
        "lead": {
            "session_id": request.session_id,
            "client_name": request.client_name,
            "phone": request.phone,
            "service": request.service,
            "preferred_time": request.preferred_time
        }
    }


@router.get("/leads")
def get_leads():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, session_id, client_name, phone, service, preferred_time, status, created_at
        FROM spa_leads
        ORDER BY created_at DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    leads = []

    for row in rows:
        leads.append({
            "id": row[0],
            "session_id": row[1],
            "client_name": row[2],
            "phone": row[3],
            "service": row[4],
            "preferred_time": row[5],
            "status": row[6],
            "created_at": str(row[7])
        })

    return {
        "total_leads": len(leads),
        "leads": leads
    }