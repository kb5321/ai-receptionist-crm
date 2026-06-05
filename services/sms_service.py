from database import get_db_connection


def save_sms_message(client_id, phone, message, status, ringcentral_message_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO sms_messages
            (client_id, phone, message, status, source, direction, ringcentral_message_id)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            client_id,
            phone,
            message,
            status,
            "RingCentral",
            "Outbound",
            str(ringcentral_message_id)
        )
    )

    conn.commit()
    cur.close()
    conn.close()