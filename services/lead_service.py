from database import get_db_connection
def create_appointment_from_lead(lead_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, client_name, phone, service, preferred_time
        FROM spa_leads
        WHERE id = %s
        """,
        (lead_id,)
    )

    lead = cur.fetchone()

    if lead is None:
        cur.close()
        conn.close()
        return False

    cur.execute(
        """
        INSERT INTO appointments
        (lead_id, client_name, phone, service, appointment_time)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            lead[0],
            lead[1],
            lead[2],
            lead[3],
            lead[4]
        )
    )

    conn.commit()
    cur.close()
    conn.close()

    return True    

def save_lead(session_id, client_name, phone, service, preferred_time):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO spa_leads
        (session_id, client_name, phone, service, preferred_time)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (session_id, client_name, phone, service, preferred_time)
    )

    conn.commit()
    cur.close()
    conn.close()
