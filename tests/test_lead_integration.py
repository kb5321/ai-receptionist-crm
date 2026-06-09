import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from database import get_db_connection
from services.lead_service import (
    save_lead,
    create_appointment_from_lead
                                   
)

#This proves:
# real spa_leads row
# ↓
# create_appointment_from_lead()
# ↓
# real appointments row created
# ↓
# cleanup removes test data

def test_save_lead_inserts_record_into_database():

    save_lead(
        session_id="integration-test",
        client_name="Tony Test",
        phone="2105559999",
        service="Massage",
        preferred_time="Tomorrow"
    )

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            session_id,
            client_name,
            phone,
            service,
            preferred_time
        FROM spa_leads
        WHERE session_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        ("integration-test",)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    assert row is not None

    assert row[0] == "integration-test"
    assert row[1] == "Tony Test"
    assert row[2] == "2105559999"
    assert row[3] == "Massage"
    assert row[4] == "Tomorrow"




def test_create_appointment_from_lead_creates_real_appointment():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO spa_leads
        (session_id, client_name, phone, service, preferred_time)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            "integration-appointment-test",
            "Integration Client",
            "2105557777",
            "Massage",
            "Tomorrow morning"
        )
    )

    lead_id = cur.fetchone()[0]
    conn.commit()

    result = create_appointment_from_lead(lead_id)

    cur.execute(
        """
        SELECT lead_id, client_name, phone, service, appointment_time
        FROM appointments
        WHERE lead_id = %s
        """,
        (lead_id,)
    )

    appointment = cur.fetchone()

    cur.execute(
        """
        DELETE FROM appointments
        WHERE lead_id = %s
        """,
        (lead_id,)
    )

    cur.execute(
        """
        DELETE FROM spa_leads
        WHERE id = %s
        """,
        (lead_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    assert result is True

    assert appointment is not None
    assert appointment[0] == lead_id
    assert appointment[1] == "Integration Client"
    assert appointment[2] == "2105557777"
    assert appointment[3] == "Massage"
    assert appointment[4] == "Tomorrow morning"