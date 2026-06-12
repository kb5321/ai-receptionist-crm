import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from database import get_db_connection


def reset_demo_data():
    conn = get_db_connection()
    cur = conn.cursor()

    print("Deleting old demo-sensitive records...")

    cur.execute("DELETE FROM sms_messages;")
    cur.execute("DELETE FROM client_notes;")
    cur.execute("DELETE FROM appointments;")
    cur.execute("DELETE FROM spa_leads;")
    cur.execute("DELETE FROM chat_messages;")
    cur.execute("DELETE FROM clients;")

    print("Inserting demo clients...")

    demo_clients = [
        ("Maria Johnson", "210-555-1001", "maria@example.com", 6, "Deep Tissue Massage"),
        ("Sarah Williams", "210-555-1002", "sarah@example.com", 4, "European Facial"),
        ("David Martinez", "210-555-1003", "david@example.com", 3, "Swedish Massage"),
        ("Emily Garcia", "210-555-1004", "emily@example.com", 8, "Manicure"),
        ("James Wilson", "210-555-1005", "james@example.com", 2, "Pedicure"),
    ]

    client_ids = {}

    for client in demo_clients:
        cur.execute(
            """
            INSERT INTO clients
                (
                    client_name,
                    phone,
                    email,
                    total_visits,
                    last_service,
                    last_appointment_date
                )
            VALUES
                (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
            """,
            client,
        )

        client_id = cur.fetchone()[0]
        client_ids[client[1]] = client_id

    print("Inserting demo leads...")

    demo_leads = [
        ("demo-session-001", "Maria Johnson", "210-555-1001", "Deep Tissue Massage", "Friday morning", "booked"),
        ("demo-session-002", "Sarah Williams", "210-555-1002", "European Facial", "Tomorrow afternoon", "contacted"),
        ("demo-session-003", "David Martinez", "210-555-1003", "Swedish Massage", "Saturday", "booked"),
        ("demo-session-004", "Emily Garcia", "210-555-1004", "Manicure", "Thursday evening", "new"),
        ("demo-session-005", "James Wilson", "210-555-1005", "Pedicure", "Next week", "new"),
    ]

    lead_ids = {}

    for lead in demo_leads:
        cur.execute(
            """
            INSERT INTO spa_leads
                (
                    session_id,
                    client_name,
                    phone,
                    service,
                    preferred_time,
                    status
                )
            VALUES
                (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            lead,
        )

        lead_id = cur.fetchone()[0]
        lead_ids[lead[2]] = lead_id

    print("Inserting demo appointments with lead_id links...")

    demo_appointments = [
        (
            lead_ids["210-555-1001"],
            "Maria Johnson",
            "210-555-1001",
            "Deep Tissue Massage",
            "2026-06-12 10:00 AM",
            "confirmed",
        ),
        (
            lead_ids["210-555-1002"],
            "Sarah Williams",
            "210-555-1002",
            "European Facial",
            "2026-06-12 1:30 PM",
            "booked",
        ),
        (
            lead_ids["210-555-1003"],
            "David Martinez",
            "210-555-1003",
            "Swedish Massage",
            "2026-06-13 11:00 AM",
            "completed",
        ),
        (
            lead_ids["210-555-1004"],
            "Emily Garcia",
            "210-555-1004",
            "Manicure",
            "2026-06-13 3:00 PM",
            "confirmed",
        ),
        (
            lead_ids["210-555-1005"],
            "James Wilson",
            "210-555-1005",
            "Pedicure",
            "2026-06-14 9:30 AM",
            "scheduled",
        ),
    ]

    for appointment in demo_appointments:
        cur.execute(
            """
            INSERT INTO appointments
                (
                    lead_id,
                    client_name,
                    phone,
                    service,
                    appointment_time,
                    status
                )
            VALUES
                (%s, %s, %s, %s, %s, %s)
            """,
            appointment,
        )

    print("Inserting demo SMS records...")

    demo_sms = [
        (
            client_ids["210-555-1001"],
            "210-555-1001",
            "Hi Maria, your Deep Tissue Massage appointment has been confirmed.",
            "Queued",
            "Outbound",
            "RingCentral",
            "demo-msg-001",
        ),
        (
            client_ids["210-555-1002"],
            "210-555-1002",
            "Hi Sarah, thank you for contacting AI Receptionist CRM.",
            "Delivered",
            "Outbound",
            "RingCentral",
            "demo-msg-002",
        ),
        (
            client_ids["210-555-1003"],
            "210-555-1003",
            "This is a friendly reminder for your upcoming appointment.",
            "Delivered",
            "Outbound",
            "RingCentral",
            "demo-msg-003",
        ),
        (
            client_ids["210-555-1004"],
            "210-555-1004",
            "Hi Emily, your manicure appointment has been confirmed.",
            "Queued",
            "Outbound",
            "RingCentral",
            "demo-msg-004",
        ),
        (
            client_ids["210-555-1005"],
            "210-555-1005",
            "Hi James, thank you for your appointment request.",
            "Delivered",
            "Outbound",
            "RingCentral",
            "demo-msg-005",
        ),
    ]

    for sms in demo_sms:
        cur.execute(
            """
            INSERT INTO sms_messages
                (
                    client_id,
                    phone,
                    message,
                    status,
                    direction,
                    source,
                    ringcentral_message_id
                )
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
            """,
            sms,
        )

    print("Inserting demo client notes...")

    demo_notes = [
        (client_ids["210-555-1001"], "Prefers deep pressure massage."),
        (client_ids["210-555-1002"], "Interested in monthly facial treatments."),
        (client_ids["210-555-1003"], "Asked about evening appointment availability."),
        (client_ids["210-555-1004"], "Prefers weekday appointments."),
        (client_ids["210-555-1005"], "New client interested in wellness packages."),
    ]

    for note in demo_notes:
        cur.execute(
            """
            INSERT INTO client_notes
                (
                    client_id,
                    note
                )
            VALUES
                (%s, %s)
            """,
            note,
        )

    print("Inserting demo chat messages...")

    demo_chat_messages = [
        ("demo-session-001", "user", "Hi, my name is Maria Johnson. I would like a deep tissue massage Friday morning."),
        ("demo-session-001", "assistant", "Thank you Maria. I added your request to the appointment waitlist."),
        ("demo-session-002", "user", "Hello, I am interested in a facial tomorrow afternoon."),
        ("demo-session-002", "assistant", "Thank you Sarah. I captured your facial appointment request."),
        ("demo-session-003", "user", "I need a Swedish massage on Saturday."),
        ("demo-session-003", "assistant", "Thank you David. Your massage request has been saved."),
    ]

    for message in demo_chat_messages:
        cur.execute(
            """
            INSERT INTO chat_messages
                (
                    session_id,
                    role,
                    content
                )
            VALUES
                (%s, %s, %s)
            """,
            message,
        )

    conn.commit()
    cur.close()
    conn.close()

    print("Demo data reset completed successfully.")


if __name__ == "__main__":
    reset_demo_data()