
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from database import get_db_connection
from services.client_service import (
    create_client_note,
    update_client_from_appointment
    )
# This proves:
# Create real client
# ↓
# create_client_note()
# ↓
# Real INSERT into client_notes
# ↓
# SELECT note
# ↓
# Verify content
# ↓
# Cleanup
def test_create_client_note_inserts_real_note():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO clients
        (
            client_name,
            phone,
            total_visits
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        (
            "Integration Client",
            "2105558888",
            1
        )
    )

    client_id = cur.fetchone()[0]

    conn.commit()

    result = create_client_note(
        client_id,
        "Integration test note"
    )

    cur.execute(
        """
        SELECT note
        FROM client_notes
        WHERE client_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (client_id,)
    )

    row = cur.fetchone()

    cur.execute(
        """
        DELETE FROM client_notes
        WHERE client_id = %s
        """,
        (client_id,)
    )

    cur.execute(
        """
        DELETE FROM clients
        WHERE id = %s
        """,
        (client_id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    assert result is True

    assert row is not None

    assert row[0] == "Integration test note"

# import sys
# from pathlib import Path

# ROOT_DIR = Path(__file__).resolve().parents[1]
# sys.path.append(str(ROOT_DIR))


# This Prove:
# Real appointment
# ↓
# update_client_from_appointment()
# ↓
# Real client row inserted
# ↓
# Verified
# ↓
# Cleaned up


def test_update_client_from_appointment_inserts_real_new_client():
    phone = "2105554444"

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM clients
        WHERE phone = %s
        """,
        (phone,)
    )

    cur.execute(
        """
        INSERT INTO appointments
        (
            client_name,
            phone,
            service,
            appointment_time,
            status
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        (
            "Integration Client",
            phone,
            "Massage",
            "2026-06-10 10:00 AM",
            "completed"
        )
    )

    appointment_id = cur.fetchone()[0]
    conn.commit()

    result = update_client_from_appointment(
        appointment_id
    )

    cur.execute(
        """
        SELECT
            client_name,
            phone,
            total_visits,
            last_service
        FROM clients
        WHERE phone = %s
        """,
        (phone,)
    )

    client = cur.fetchone()

    cur.execute(
        """
        DELETE FROM appointments
        WHERE id = %s
        """,
        (appointment_id,)
    )

    cur.execute(
        """
        DELETE FROM clients
        WHERE phone = %s
        """,
        (phone,)
    )

    conn.commit()
    cur.close()
    conn.close()

    assert result is True

    assert client is not None
    assert client[0] == "Integration Client"
    assert client[1] == phone
    assert client[2] == 1
    assert client[3] == "Massage"