from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from services.appointment_service import (
    update_appointment_status_service,
    get_all_appointments,
    get_admin_appointments_page,
    
)

# =====================================
# Router
# =====================================

router = APIRouter()


@router.get("/appointments")
def get_appointments():
    return get_all_appointments()


@router.get("/admin/appointments", response_class=HTMLResponse)
def admin_appointments(request: Request):
    return get_admin_appointments_page(request)


@router.put("/appointments/{appointment_id}/status")
def update_appointment_status(appointment_id: int, status: str):
    result = update_appointment_status_service(appointment_id, status)

    return {
        "message": "Appointment status updated",
        **result
    }


# # -------------------------------------------------------------
# @router.get("/appointments")
# def get_appointments():

#     conn = get_db_connection()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         SELECT
#         id,
#         lead_id,
#         client_name,
#         phone,
#         service,
#         appointment_time,
#         status,
#         created_at
#         FROM appointments
#         ORDER BY created_at DESC
#         """
#     )

#     rows = cur.fetchall()

#     cur.close()
#     conn.close()

#     appointments = []

#     for row in rows:
#         appointments.append({
#             "id": row[0],
#             "lead_id": row[1],
#             "client_name": row[2],
#             "phone": row[3],
#             "service": row[4],
#             "appointment_time": row[5],
#              "status": row[6],
#             "created_at": str(row[7])
#         })

#     return {
#         "total_appointments": len(appointments),
#         "appointments": appointments
#     }

# # -------------------------------------------------------------

# @router.get("/admin/appointments", response_class=HTMLResponse)
# def leads_admin_page(request: Request):
#     if not require_login(request):
#         return RedirectResponse(url="/admin/login", status_code=302)
#     return """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Terra Spa Appointments</title>
#         <style>
#             body { font-family: Arial; margin: 40px; }
#             table { border-collapse: collapse; width: 100%; }
#             th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
#             th { background-color: #f2f2f2; }
#         </style>
#     </head>
#     <body>
#         <div style="margin-bottom:20px;">
#             <a href="/admin">🏠 Admin Home</a>
#             &nbsp;&nbsp;&nbsp;
#             <a href="/admin/logout">Logout</a>
#         </div>
#         <h2>Terra Spa Appointments</h2>

#         <table>
#             <thead>
#                 <tr>
#                     <th>ID</th>
#                     <th>Lead ID</th>
#                     <th>Client Name</th>
#                     <th>Phone</th>
#                     <th>Service</th>
#                     <th>Appointment Time</th>
#                     <th>Status</th>
#                     <th>Created At</th>
#                 </tr>
#             </thead>
#             <tbody id="appointmentsTable"></tbody>
#         </table>

#         <script>
#             async function loadAppointments() {
#                 const response = await fetch("/appointments");
#                 const data = await response.json();

#                 const table = document.getElementById("appointmentsTable");
#                 table.innerHTML = "";

#                 data.appointments.forEach(appt => {
#                     const row = document.createElement("tr");

#                     row.innerHTML = `
#                         <td>${appt.id}</td>
#                         <td>${appt.lead_id}</td>
#                         <td>${appt.client_name}</td>
#                         <td>${appt.phone}</td>
#                         <td>${appt.service}</td>
#                         <td>${appt.appointment_time}</td>

#                         <td>
#                             <select onchange="updateAppointmentStatus(${appt.id}, this.value)">
#                                 <option value="scheduled" ${appt.status === "scheduled" ? "selected" : ""}>scheduled</option>
#                                 <option value="confirmed" ${appt.status === "confirmed" ? "selected" : ""}>confirmed</option>
#                                 <option value="checked_in" ${appt.status === "checked_in" ? "selected" : ""}>checked_in</option>
#                                 <option value="completed" ${appt.status === "completed" ? "selected" : ""}>completed</option>
#                                 <option value="cancelled" ${appt.status === "cancelled" ? "selected" : ""}>cancelled</option>
#                                 <option value="no_show" ${appt.status === "no_show" ? "selected" : ""}>no_show</option>
#                             </select>
#                         </td>


#                         <td>${appt.created_at}</td>
#                     `;

#                     table.appendChild(row);
#                 });
#             }

#             loadAppointments();
#             async function updateAppointmentStatus(appointmentId, status) {

#                 await fetch(
#                     `/appointments/${appointmentId}/status?status=${status}`,
#                     {
#                         method: "PUT"
#                     }
#                 );

#                 loadAppointments();
#             }

#         </script>
#     </body>
#     </html>
#     """
# # -------------------------------------------------------------


# # code from yesterday 

# @router.put("/appointments/{appointment_id}/status")
# def update_appointment_status(appointment_id: int, status: str):
#     result = update_appointment_status_service(appointment_id, status)

#     return {
#         "message": "Appointment status updated",
#         **result
#     }

# @router.put("/appointments/{appointment_id}/status")
# def update_appointment_status(appointment_id: int, status: str):

#     conn = get_db_connection()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         UPDATE appointments
#         SET status = %s
#         WHERE id = %s
#         """,
#         (status, appointment_id)
#     )

#     updated_count = cur.rowcount

#     conn.commit()

#     client_updated = False

#     if status == "completed":
#         client_updated = update_client_from_appointment(
#             appointment_id
#         )

#     sms_created = False

#     if status == "confirmed":
#         conn = get_db_connection()
#         cur = conn.cursor()

#         cur.execute(
#             """
#             SELECT client_name, phone, service, appointment_time
#             FROM appointments
#             WHERE id = %s
#             """,
#             (appointment_id,)
#         )

#         appointment = cur.fetchone()

#         cur.close()
#         conn.close()

#         if appointment:
#             client_name = appointment[0]
#             phone = appointment[1]
#             service = appointment[2]
#             appointment_time = appointment[3]

#             message = (
#                 f"Hi {client_name}, your Terra Spa {service} appointment "
#                 f"request for {appointment_time} has been confirmed."
#             )


#             sms_created = False
#             sms_sent = False

#             try:
#                 result = send_sms(phone, message)

#                 save_sms_message(
#                     client_id=None,
#                     phone=phone,
#                     message=message,
#                     status=result.get("messageStatus"),
#                     ringcentral_message_id=result.get("id")
#                 )

#                 sms_created = True
#                 sms_sent = True

#             except Exception as e:
#                 print("SMS send failed:", e)

#     return {
#         "message": "Appointment status updated",
#         "appointment_id": appointment_id,
#         "new_status": status,
#         "updated_count": updated_count,
#         "client_updated": client_updated,
#         "sms_created": sms_created,
#         "sms_sent": sms_sent
        
#     }
