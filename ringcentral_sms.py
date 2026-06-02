from dotenv import load_dotenv
import os
import psycopg2

from ringcentral import SDK

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_platform():
    rcsdk = SDK(
        os.getenv("RINGCENTRAL_CLIENT_ID"),
        os.getenv("RINGCENTRAL_CLIENT_SECRET"),
        os.getenv("RINGCENTRAL_SERVER_URL")
    )

    platform = rcsdk.platform()
    platform.login(jwt=os.getenv("RINGCENTRAL_JWT"))

    return platform


def send_sms(to_number: str, message: str):
    platform = get_platform()

    response = platform.post(
        "/restapi/v1.0/account/~/extension/~/sms",
        {
            "from": {
                "phoneNumber": os.getenv("RINGCENTRAL_FROM_NUMBER")
            },
            "to": [
                {
                    "phoneNumber": to_number
                }
            ],
            "text": message
        }
    )

    return response.json_dict()


def save_sms_message(client_id, phone, message, status, ringcentral_message_id):
    conn = psycopg2.connect(DATABASE_URL)
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


if __name__ == "__main__":
    test_to_number = "+12102940217"
    test_message = "Test SMS from Terra Spa CRM using Extension 106."

    result = send_sms(test_to_number, test_message)

    save_sms_message(
        client_id=None,
        phone=test_to_number,
        message=test_message,
        status=result.get("messageStatus"),
        ringcentral_message_id=result.get("id")
    )

    print("SMS sent successfully")
    print("RingCentral Message ID:", result.get("id"))
    print("Status:", result.get("messageStatus"))
    print("Saved to database")