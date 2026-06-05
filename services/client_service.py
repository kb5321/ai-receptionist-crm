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