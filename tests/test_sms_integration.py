import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from database import get_db_connection
from services.sms_service import save_sms_message


def test_save_sms_message_inserts_real_sms_log():
    phone = "2105556666"
    message = "Integration test SMS"
    ringcentral_message_id = "integration-test-123"

    save_sms_message(
        client_id=None,
        phone=phone,
        message=message,
        status="Queued",
        ringcentral_message_id=ringcentral_message_id
    )

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            client_id,
            phone,
            message,
            status,
            source,
            direction,
            ringcentral_message_id
        FROM sms_messages
        WHERE ringcentral_message_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (ringcentral_message_id,)
    )

    row = cur.fetchone()

    cur.execute(
        """
        DELETE FROM sms_messages
        WHERE ringcentral_message_id = %s
        """,
        (ringcentral_message_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    assert row is not None

    assert row[0] is None
    assert row[1] == phone
    assert row[2] == message
    assert row[3] == "Queued"
    assert row[4] == "RingCentral"
    assert row[5] == "Outbound"
    assert row[6] == ringcentral_message_id

    #-----------------------------
#     This proves:
#     save_sms_message()
# ↓
#     real INSERT into sms_messages
#     ↓
#     real SELECT
#     ↓
#     data verified
#     ↓
#     cleanup DELETE