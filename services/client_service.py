from database import get_db_connection
def create_client_note(client_id, note):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO client_notes
        (client_id, note)
        VALUES (%s, %s)
        """,
        (client_id, note)
    )

    conn.commit()

    cur.close()
    conn.close()

    return True

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


