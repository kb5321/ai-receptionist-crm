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

