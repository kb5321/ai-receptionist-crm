from auth import require_login
class MockRequest:
    def __init__(self, cookies):
        self.cookies = cookies


def test_require_login_returns_true():

    request = MockRequest(
        {"admin_logged_in": "true"}
    )

    assert require_login(request) is True
#What are we testing? Cookie exists Value = "true" Expected:      True


def test_require_login_returns_false_when_cookie_missing():

    request = MockRequest({})

    assert require_login(request) is False
#What are we testing? Cookie missing Expected: False

def test_require_login_returns_false_when_cookie_invalid():

    request = MockRequest(
        {"admin_logged_in": "false"}
    )

    assert require_login(request) is False
#What are we testing? Cookie exists Wrong value  Expected:     False
     