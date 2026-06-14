import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from main import app

client = TestClient(app)


def test_admin_clients_requires_login():
    response = client.get(
        "/admin/clients",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"

def test_admin_leads_requires_login():

    response = client.get(
        "/admin/leads",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"



def test_admin_appointments_requires_login():
    """
    Purpose:
        Verify that unauthenticated users cannot access
        the Admin Appointments page.

    Scenario:
        A user attempts to visit /admin/appointments
        without a valid login session.

    Expected Result:
        The server responds with HTTP 302 and
        redirects the user to /admin/login.

    What We Are Testing:
        Authentication enforcement.

    Why This Matters:
        Appointment data contains customer and
        scheduling information that should only
        be accessible to authorized staff.

    Test Type:
        Security Test
        Authentication Test
    """

    response = client.get(
        "/admin/appointments",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"


def test_admin_sms_requires_login():
    """
    Purpose:
        Verify that unauthenticated users cannot access
        the SMS administration page.

    Scenario:
        A user attempts to visit /admin/sms
        without being logged in.

    Expected Result:
        The server responds with HTTP 302 and
        redirects the user to /admin/login.

    What We Are Testing:
        Authentication enforcement.

    Why This Matters:
        SMS history may contain customer phone
        numbers and private communications.

        Unauthorized access would be a security risk.

    Test Type:
        Security Test
        Authentication Test
    """

    response = client.get(
        "/admin/sms",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"

def test_admin_login_page_loads():
    """
    Purpose:
        Verify that the login page is available
        and contains the login form.

    Scenario:
        A user navigates to /admin/login.

    Expected Result:
        The page loads successfully and displays
        the login form.

    What We Are Testing:
        Login page availability.

    Why This Matters:
        If the login page fails to load,
        administrators cannot access the CRM.

    Technical Verification:
        1. HTTP 200 returned.
        2. Login page title exists.
        3. Login form exists.
        4. Form submits to /admin/login.

    Test Type:
        UI Endpoint Test
        Authentication Test
    """
    response = client.get("/admin/login")

    assert response.status_code == 200
    assert "Demo Wellness Center Admin Login" in response.text
    assert '<form method="post" action="/admin/login">' in response.text


# =====================================================
# Authentication Test
# =====================================================

def test_admin_clients_redirects_to_login_page():
    """
    Purpose:
        Verify that an unauthenticated user cannot access
        the Admin Clients page.

    Scenario:
        A user visits /admin/clients without being logged in.

    Expected Result:
        The application redirects the user to the login page.
        Since TestClient follows redirects by default,
        the final response should be the login page.

    What We Are Testing:
        Authentication protection.

    Why This Matters:
        Prevents unauthorized users from viewing
        client information.
    """

    response = client.get(
        "/admin/clients"
    )

    assert response.status_code == 200

    assert "Demo Wellness Center Admin Login" in response.text



# =====================================================
# Logout Test
# =====================================================

def test_admin_logout_redirects_to_login():
    """
    Purpose:
        Verify that the logout route redirects users
        to the login page.

    Scenario:
        A user clicks Logout.

    Expected Result:
        The application returns an HTTP 302 redirect
        to /admin/login.

    What We Are Testing:
        Logout navigation behavior.

    Why This Matters:
        Ensures users are sent to the correct page
        after logging out.
    """

    response = client.get(
        "/admin/logout",
        follow_redirects=False
    )

    assert response.status_code == 302

    assert response.headers["location"] == "/admin/login"
    

# =====================================================
# Logout Security Test
# =====================================================

def test_admin_logout_deletes_cookie_header():
    """
    Purpose:
        Verify that logout removes the authentication cookie.

    Scenario:
        A user logs out of the application.

    Expected Result:
        The response contains a Set-Cookie header
        instructing the browser to delete the
        admin_logged_in cookie.

    What We Are Testing:
        Logout security behavior.

    Why This Matters:
        Logging out should invalidate the user's
        authenticated session.

        If the cookie is not removed, the browser
        may remain authenticated.

    Technical Detail:
        We inspect the response header instead of
        the browser cookie store because the server
        controls the cookie deletion instruction.
    """

    response = client.get(
        "/admin/logout",
        follow_redirects=False
    )

    assert response.status_code == 302

    assert response.headers["location"] == "/admin/login"

    set_cookie_header = response.headers.get(
        "set-cookie",
        ""
    )

    assert "admin_logged_in" in set_cookie_header

    assert (
        "Max-Age=0" in set_cookie_header
        or
        "expires=" in set_cookie_header.lower()
    )

