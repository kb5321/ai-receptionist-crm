from dotenv import load_dotenv
load_dotenv()
import os
from ringcentral import SDK

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

    

    if __name__ == "__main__":
        from services.sms_service import save_sms_message

        test_to_number = os.getenv("TEST_SMS_TO_NUMBER")
        test_message = "Dev test message."

        if not test_to_number:
            raise ValueError("TEST_SMS_TO_NUMBER is not configured")
        
        

        result =send_sms(test_to_number, test_message)

        if not result:
            raise RuntimeError("SMS send failed")
     
        save_sms_message(
            client_id=None,
            phone=test_to_number,
            message=test_message,
            status=result.get("messageStatus"),
            ringcentral_message_id=result.get("id")
        )