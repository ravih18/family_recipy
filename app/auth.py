import os
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
APP_PASSWORD = os.getenv("APP_PASSWORD", "famille")
COOKIE_NAME = "session"

serializer = URLSafeSerializer(SECRET_KEY)


def create_session_cookie() -> str:
    return serializer.dumps({"authenticated": True})


def is_authenticated(request: Request) -> bool:
    cookie = request.cookies.get(COOKIE_NAME)
    if not cookie:
        return False
    try:
        data = serializer.loads(cookie)
        return data.get("authenticated") is True
    except BadSignature:
        return False


def require_auth(request: Request):
    """Dépendance FastAPI : redirige vers /login si non authentifié."""
    if not is_authenticated(request):
        raise HTTPException(status_code=307, headers={"Location": "/login"})