# auth.py

from fastapi import Request


def require_login(request: Request):
    return request.cookies.get("admin_logged_in") == "true"


def get_admin_role(request: Request):
    return request.cookies.get("admin_role")


def require_role(request: Request, required_role: str):
    return get_admin_role(request) == required_role


def require_admin(request: Request):
    return require_role(request, "admin")

