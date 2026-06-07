from auth import (
    get_admin_role,
    require_role,
    require_admin
)

class MockRequest:
    def __init__(self, cookies):
        self.cookies = cookies

def test_get_admin_role_returns_admin():
    """
    Purpose:
        Verify that get_admin_role()
        returns the role stored in the cookie.

    Scenario:
        User has admin_role=admin cookie.

    Expected Result:
        Function returns "admin".

    Test Type:
        Unit Test
    """

    request = MockRequest(
        {"admin_role": "admin"}
    )

    assert get_admin_role(request) == "admin"

def test_get_admin_role_returns_none_when_missing():
    """
    Purpose:
        Verify behavior when role cookie
        does not exist.

    Expected Result:
        None is returned.

    Test Type:
        Unit Test
    """

    request = MockRequest({})

    assert get_admin_role(request) is None

def test_require_role_returns_true_for_matching_role():
    """
    Purpose:
        Verify that require_role()
        grants access when roles match.

    Scenario:
        User role = admin
        Required role = admin

    Expected Result:
        True

    Test Type:
        Authorization Unit Test
    """

    request = MockRequest(
        {"admin_role": "admin"}
    )

    assert require_role(
        request,
        "admin"
    ) is True


def test_require_role_returns_false_for_wrong_role():
    """
    Purpose:
        Verify that require_role()
        denies access when roles differ.

    Scenario:
        User role = staff
        Required role = admin

    Expected Result:
        False

    Test Type:
        Authorization Unit Test
    """

    request = MockRequest(
        {"admin_role": "staff"}
    )

    assert require_role(
        request,
        "admin"
    ) is False


def test_require_admin_returns_true():
    """
    Purpose:
        Verify that admin users
        pass require_admin().

    Expected Result:
        True

    Test Type:
        Authorization Unit Test
    """

    request = MockRequest(
        {"admin_role": "admin"}
    )

    assert require_admin(request) is True

def test_require_admin_returns_false():
    """
    Purpose:
        Verify that non-admin users
        fail require_admin().

    Expected Result:
        False

    Test Type:
        Authorization Unit Test
    """

    request = MockRequest(
        {"admin_role": "staff"}
    )

    assert require_admin(request) is False