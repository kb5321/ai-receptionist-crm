from fastapi import APIRouter

router = APIRouter()


@router.get("/test-users")
def test_users():
    return {"status": "users router working"}