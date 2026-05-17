from __future__ import annotations

import secrets
from typing import Any

from starlette.requests import Request

from app.core.config import get_settings


SESSION_USER_KEY = "demo_user"


def authenticate(username: str, password: str) -> bool:
    settings = get_settings()
    return secrets.compare_digest(username, settings.demo_username) and secrets.compare_digest(
        password,
        settings.demo_password,
    )


def login_user(request: Request, username: str) -> None:
    request.session[SESSION_USER_KEY] = username


def logout_user(request: Request) -> None:
    request.session.pop(SESSION_USER_KEY, None)


def get_current_user(request: Request) -> str | None:
    user = request.session.get(SESSION_USER_KEY)
    return str(user) if user else None


def template_context(request: Request, **extra: Any) -> dict[str, Any]:
    return {
        "request": request,
        "current_user": get_current_user(request),
        **extra,
    }
