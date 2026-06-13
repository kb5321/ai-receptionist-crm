from fastapi import FastAPI, HTTPException,Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
#from ringcentral_sms import send_sms

from config import DATABASE_URL, OPENAI_API_KEY
from auth import (
    require_login,
    require_admin,
    require_role,
    get_admin_role
)

from pydantic import BaseModel
from openai import OpenAI
from passlib.hash import pbkdf2_sha256
import re
import os
import traceback


from database import get_db_connection
from routers import users
from routers import clients
from routers import leads
from routers import appointments
from routers import sms
from routers import audit_router


from audit import save_audit_log
from services.lead_service import save_lead

# =====================================
# Application Version
# =====================================

APP_VERSION = "1.0.0"



app = FastAPI()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app.include_router(users.router)
app.include_router(clients.router)
app.include_router(leads.router)
app.include_router(appointments.router)
app.include_router(sms.router)
app.include_router(audit_router.router)

# Demo business knowledge used for AI receptionist behavior.
# Production deployments should load business-specific data from a database or configuration.

BUSINESS_KNOWLEDGE = """
Business Name: Demo Wellness Center

Business Type:
A wellness and personal care business offering appointment-based services.

Current Status:
Accepting inquiries and appointment requests.

Booking Policy:
Clients may submit appointment requests and will be contacted for confirmation.

Gift Certificates:
Clients should provide their name, phone number, and gift certificate details.

Client Communication Style:
Be polite, calm, professional, and helpful. Keep answers short and clear.

Important Rules:

* Do not invent prices.
* Do not invent appointment availability.
* Do not provide medical advice.
* If important booking information is missing, ask for the client's name, phone number, preferred service, and preferred time.
* If the client already provided booking details, confirm the request was received and saved.
* If the client wants to book, explain that appointment requests are reviewed and clients will be contacted with availability and confirmation details.

"""


class AskRequest(BaseModel):
    session_id: str
    question: str


def save_message(role, content, session_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO chat_messages (role, content, session_id)
        VALUES (%s, %s, %s)
        """,
        (role, content, session_id)
    )

    conn.commit()
    cur.close()
    conn.close()


def load_recent_messages(session_id, limit=10):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, content
        FROM chat_messages
        WHERE session_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (session_id, limit)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    rows.reverse()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]


def extract_lead_info(question):
    text = question.lower()

    
    services = [
        "massage",
        "facial",
        "waxing",
        "nails",
        "bodywrap",
        "body wrap",
        "pedicure",
        "manicure"
    ]
    service = "Unknown"

    for s in services:
        if s in text:
            service = s
            break

    
    phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", question )

    if phone_match:
        raw_phone = phone_match.group(0)
        digits = re.sub(r"\D", "", raw_phone)

        if len(digits) == 10:
            phone = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        else:
            phone = "Unknown"
    else:
        phone = "Unknown"

    preferred_time = "Unknown"

    date_time_match = re.search(
        r"\b("
        r"january|february|march|april|may|june|july|august|"
        r"september|october|november|december"
        r")\s+\d{1,2}"
        r"(\s+(morning|afternoon|evening|at\s+\d{1,2}(:\d{2})?\s*(am|pm)?))?",
        text,
        re.IGNORECASE
    )

    if date_time_match:
        preferred_time = date_time_match.group(0).strip()
    else:
        time_keywords = [
            "today",
            "tomorrow",
            "morning",
            "afternoon",
            "evening",
            "friday",
            "saturday",
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday"
        ]

        for word in time_keywords:
            if word in text:
                preferred_time = word
                break    

    client_name = "Unknown"

    name_match = re.search(r"my name is ([A-Za-z\s]+)", question, re.IGNORECASE)
    if name_match:
        client_name = name_match.group(1).strip()

    return client_name, phone, service, preferred_time


@app.get("/")
def root():
    return {"message": "Hello AI Infrastructure World"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database_configured": DATABASE_URL is not None,
        "openai_configured": OPENAI_API_KEY is not None
    }

@app.get("/version")
def version():
    return {
        "app": "AI Receptionist CRM",
        "version": APP_VERSION,
        "environment": "production"
    }


@app.get("/messages")
def get_messages():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, session_id, role, content, created_at
        FROM chat_messages
        ORDER BY created_at DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    messages = []

    for row in rows:
        messages.append({
            "id": row[0],
            "session_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": str(row[4])
        })

    return {
        "total_messages": len(messages),
        "messages": messages
    }

@app.get("/messages/{session_id}")
def get_messages_by_session(session_id: str):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, session_id, role, content, created_at
        FROM chat_messages
        WHERE session_id = %s
        ORDER BY created_at ASC
        """,
        (session_id,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    messages = []

    for row in rows:
        messages.append({
            "id": row[0],
            "session_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": str(row[4])
        })

    return {
        "session_id": session_id,
        "total_messages": len(messages),
        "messages": messages
    }

@app.get("/sessions")
def get_sessions():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            session_id,
            COUNT(*) AS message_count,
            MAX(created_at) AS last_message_at
        FROM chat_messages
        WHERE session_id IS NOT NULL
        GROUP BY session_id
        ORDER BY last_message_at DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    sessions = []

    for row in rows:
        sessions.append({
            "session_id": row[0],
            "message_count": row[1],
            "last_message_at": str(row[2])
        })

    return {
        "total_sessions": len(sessions),
        "sessions": sessions
    }

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM chat_messages
        WHERE session_id = %s
        """,
        (session_id,)
    )

    deleted_count = cur.rowcount

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "Session deleted successfully",
        "session_id": session_id,
        "deleted_messages": deleted_count
    }

@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Chat</title>

        <style>
            body {
                font-family: Arial;
                margin: 40px;
            }

            #chatBox {
                border: 1px solid #ccc;
                height: 400px;
                overflow-y: scroll;
                padding: 10px;
                margin-bottom: 20px;
            }

            .user {
                color: blue;
                margin-bottom: 10px;
            }

            .assistant {
                color: green;
                margin-bottom: 20px;
            }

            textarea {
                width: 100%;
            }
        </style>
    </head>

    <body>

        <h2>AI Receptionist CRM - Chat</h2> 

        <label>Session ID:</label>
        <input id="sessionId" value="test-001" />

        <br><br>

        <div id="chatBox"></div>

        <textarea
            id="question"
            rows="4"
            placeholder="Ask a question..."
            onkeydown="handleKey(event)"
        ></textarea>

        <p id="status"></p>

        <br><br>

        <button onclick="askAI()">Send</button>

        <script>

            async function loadMessages() {

                const sessionId =
                    document.getElementById("sessionId").value;

                const response =
                    await fetch(`/messages/${sessionId}`);

                const data = await response.json();

                const chatBox =
                    document.getElementById("chatBox");

                chatBox.innerHTML = "";

                data.messages.forEach(msg => {

                    const div = document.createElement("div");

                    div.className = msg.role;

                    div.innerHTML =
                        "<b>" + msg.role + ":</b> " + msg.content;

                    chatBox.appendChild(div);
                });

                chatBox.scrollTop = chatBox.scrollHeight;
            }

            function handleKey(event) {

                if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    askAI();
                }
            }


            async function askAI() {

                const sessionId =
                    document.getElementById("sessionId").value;

                const question =
                    document.getElementById("question").value;
                    document.getElementById("status").textContent = "AI is typing...";

                await fetch("/ask", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        question: question
                    })
                });

                document.getElementById("question").value = "";

                loadMessages();
            }

            loadMessages();
            document.getElementById("status").textContent = "";

        </script>

    </body>
    </html>
    """


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):

    if not require_login(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    return """
    <!DOCTYPE html>

<html>
<head>
    
    <title>AI Receptionist CRM Dashboard</title>


<style>
    body {
        font-family: Arial;
        margin: 40px;
    }

    .top-nav {
        margin-bottom: 25px;
    }

    .top-nav a {
        text-decoration: none;
        margin-right: 20px;
        font-size: 16px;
        font-weight: bold;
    }

    .menu {
        margin-top: 30px;
        width: 350px;
    }

    .menu a {
        display: block;
        padding: 12px;
        margin-bottom: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        text-decoration: none;
        font-size: 18px;
    }

    .menu a:hover {
        background-color: #f2f2f2;
    }
</style>


</head>

<body>


<div class="top-nav">
    <a href="/admin">🏠 Dashboard</a>
    <a href="/admin/logout">🚪 Logout</a>
</div>

<h2>AI Receptionist CRM Dashboard</h2>

<div class="menu">
    <a href="/admin/leads">📋 Leads</a>
    <a href="/admin/appointments">📅 Appointments</a>
    <a href="/admin/clients">👥 Clients</a>
    <a href="/admin/sms">💬 Messages</a>
    <a href="/admin/users">🔐 Users</a>
    <a href="/admin/audit-log">📜 Audit Log</a>
</div>

</body>
</html>

    """

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Receptionist CRM - Admin Login</title>

        <style>
            body {
                font-family: Arial;
                margin: 50px;
            }

            form {
                width: 300px;
            }

            input {
                width: 100%;
                padding: 8px;
                margin-top: 10px;
            }

            button {
                margin-top: 10px;
                padding: 8px 15px;
            }
        </style>
    </head>

    <body>

        <h2>AI Receptionist CRM - Admin Login</h2>

        <form method="post" action="/admin/login">

            <input
                type="text"
                name="username"
                placeholder="Username"
                required
            >

            <input
                type="password"
                name="password"
                placeholder="Password"
                required
            >

            <button type="submit">
                Login
            </button>

        </form>

    </body>
    </html>
    """

@app.get("/admin/logout")
def admin_logout():

    response = RedirectResponse(
        url="/admin/login",
        status_code=302
    )

    response.delete_cookie("admin_logged_in")

    return response





@app.post("/admin/login")
def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT username,
               password_hash,
               role,
               is_active
        FROM admin_users
        WHERE username = %s
        """,
        (username,)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if user is None:

        return HTMLResponse(
            content="<h3>Invalid login. <a href='/admin/login'>Try again</a></h3>",
            status_code=401
        )

    db_username = user[0]
    password_hash = user[1]
    role = user[2]
    is_active = user[3]

    if not is_active:

        return HTMLResponse(
            content="<h3>Account disabled.</h3>",
            status_code=403
        )

    if not pbkdf2_sha256.verify(password, password_hash):

        return HTMLResponse(
            content="<h3>Invalid login. <a href='/admin/login'>Try again</a></h3>",
            status_code=401
        )

    response = RedirectResponse(
        url="/admin",
        status_code=302
    )

    response.set_cookie(
        key="admin_logged_in",
        value="true",
        httponly=True,
        samesite="lax"
    )

    response.set_cookie(
        key="admin_username",
        value=db_username,
        httponly=True,
        samesite="lax"
    )

    response.set_cookie(
        key="admin_role",
        value=role,
        httponly=True,
        samesite="lax"
    )

    save_audit_log(
        request,
        "LOGIN",
        f"User {db_username} logged in",
        username_override=db_username
    )

    return response



@app.post("/ask")
def ask_ai(request: AskRequest):
    try:
        previous_messages = load_recent_messages(request.session_id)

        messages = [
            {
                "role": "system",
                "content": f"""
                You are a professional AI receptionist.

                Use the following business knowledge when answering clients:

                {BUSINESS_KNOWLEDGE}
                """
            }
        ]

        messages.extend(previous_messages)

        messages.append(
            {
                "role": "user",
                "content": request.question
            }
        )

        save_message(
            "user",
            request.question,
            request.session_id
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4
        )

        ai_answer = response.choices[0].message.content

        booking_keywords = [
            "book",
            "appointment",
            "schedule",
            "waitlist",
            "facial",
            "massage",
            "waxing",
            "nails",
            "bodywrap",
            "body wrap"
        ]

        lead_saved = False

        conversation_text = " ".join(
            msg["content"] for msg in previous_messages
        ) + " " + request.question

        if any(word in conversation_text.lower() for word in booking_keywords):
            client_name, phone, service, preferred_time = extract_lead_info(
                conversation_text
            )

            last_assistant_message = ""

            for msg in reversed(previous_messages):
                if msg["role"] == "assistant":
                    last_assistant_message = msg["content"].lower()
                    break

            current_answer = request.question.strip()

            awaiting_name = (
                "provide your name" in last_assistant_message
            )

            awaiting_service = (
                "what service" in last_assistant_message
                or "service would you like" in last_assistant_message
            )

            if awaiting_name:
                client_name = current_answer.title()

            if awaiting_service:
                service = current_answer.lower()

            if service == "body wrap":
                service = "bodywrap"

            if phone == "Unknown":
                ai_answer = (
                    "I wasn't able to identify a valid phone number. "
                    "Could you please provide a 10-digit phone number "
                    "so I can save your appointment request?"
                )

                lead_saved = False

            elif client_name == "Unknown":
                ai_answer = (
                    "I have your service request and phone number. "
                    "Could you please provide your name so I can save your appointment request?"
                )

                lead_saved = False

            elif service == "Unknown":
                ai_answer = (
                    "I have your name, phone number, and preferred appointment time. "
                    "What service would you like to book?"
                )

                lead_saved = False

            else:
                if preferred_time != "Unknown":
                    #capitalize
                    preferred_time = preferred_time.title

                save_lead(
                    request.session_id,
                    client_name,
                    phone,
                    service,
                    preferred_time
                )

                ai_answer = (
                    f"Thank you, {client_name}. I have saved your appointment request "
                    f"for {service} on {preferred_time}. Your request will be reviewed, "
                    "and you will be contacted with availability and confirmation details soon."
                )

                lead_saved = True

        save_message(
            "assistant",
            ai_answer,
            request.session_id
        )

        return {
            "session_id": request.session_id,
            "question": request.question,
            "answer": ai_answer,
            "messages_used_from_database": len(previous_messages),
            "lead_saved": lead_saved
        }

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

# @app.post("/ask")
# def ask_ai(request: AskRequest):
#     try:
#         previous_messages = load_recent_messages(request.session_id)

#         messages = [
#             {
#                 "role": "system",
#                 "content": f"""
#                 You are a professional AI receptionist for Terra Spa.

#                 Use the following business knowledge when answering clients:

#                 {BUSINESS_KNOWLEDGE}
#                 """
#             }
#         ]

#         messages.extend(previous_messages)

#         messages.append(
#             {
#                 "role": "user",
#                 "content": request.question
#             }
#         )

#         save_message(
#             "user",
#             request.question,
#             request.session_id
#         )

#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages,
#             temperature=0.4
#         )

#         ai_answer = response.choices[0].message.content

#         booking_keywords = [
#             "book",
#             "appointment",
#             "schedule",
#             "waitlist",
#             "facial",
#             "massage",
#             "waxing",
#             "nails"
#         ]

#         lead_saved = False

#         conversation_text = " ".join(
#             msg["content"] for msg in previous_messages
#         ) + " " + request.question

#         print("\nCONVERSATION TEXT:")
#         print(conversation_text)
#         print()
 
#         if any(word in conversation_text.lower() for word in booking_keywords):
#             client_name, phone, service, preferred_time = extract_lead_info(
#                 conversation_text
#             )

#             if service == "body wrap":
#                 service = "bodywrap"


#             last_assistant_message = ""

#             for msg in reversed(previous_messages):
#                 if msg["role"] == "assistant":
#                     last_assistant_message = msg["content"].lower()
#                     break

#             current_answer = request.question.strip()

#             if (
#                 client_name == "Unknown"
#                 and "name" in last_assistant_message
#                 and "provide" in last_assistant_message
#             ):
#                 client_name = current_answer.title()

#             if (
#                 service == "Unknown"
#                 and "service" in last_assistant_message
#                 and "book" in last_assistant_message
#             ):
#                 service = current_answer.title()

#             print("PHONE:", phone)
#             print("NAME:", client_name)
#             print("SERVICE:", service)
#             print("TIME:", preferred_time)

#             if phone == "Unknown":
#                 ai_answer = (
#                     "I wasn't able to identify a valid phone number. "
#                     "Could you please provide a 10-digit phone number "
#                     "so I can save your appointment request?"
#                 )
            
#                 lead_saved = False

#             elif client_name == "Unknown":
#                 ai_answer = (
#                     "I have your service request and phone number. "
#                     "Could you please provide your name so I can save your appointment request?"
#                 )
            
#                 lead_saved = False

#             elif service == "Unknown":
#                 ai_answer = (
#                     "I have your name, phone number, and preferred appointment time. "
#                     "What service would you like to book?"
#                 )

#                 lead_saved = False


#             else:
#                 save_lead(
#                     request.session_id,
#                     client_name,
#                     phone,
#                     service,
#                     preferred_time
#                 )

#                 ai_answer = (
#                     f"Thank you, {client_name}. I have saved your appointment request "
#                     f"for {service} on {preferred_time}. Your request will be reviewed, "
#                     "and you will be contacted with availability and confirmation details soon."
#                 )

#                 lead_saved = True

#         save_message(
#             "assistant",
#             ai_answer,
#             request.session_id
#         )

#         return {
#             "session_id": request.session_id,
#             "question": request.question,
#             "answer": ai_answer,
#             "messages_used_from_database": len(previous_messages),
#             "lead_saved": lead_saved
#         }

#     # except Exception as e:
#     #     raise HTTPException(
#     #         status_code=500,
#     #         detail=str(e)
#     #     )
#     except Exception as e:
#         traceback.print_exc()

#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#     )
    
    