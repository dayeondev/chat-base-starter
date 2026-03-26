import os
from typing import Optional

from fastapi import Header, HTTPException, status


GATEWAY_SECRET = os.getenv("GATEWAY_SECRET", "chat-base-starter-gateway-secret-2026")


class AuthenticatedUser(dict):
    @property
    def user_id(self) -> int:
        return self["user_id"]

    @property
    def username(self) -> str:
        return self["username"]


def require_gateway_user(
    x_gateway_secret: Optional[str] = Header(default=None),
    x_user_id: Optional[str] = Header(default=None),
    x_username: Optional[str] = Header(default=None),
) -> AuthenticatedUser:
    if x_gateway_secret != GATEWAY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gateway secret"
        )

    if not x_user_id or not x_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user headers"
        )

    try:
        user_id = int(x_user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id"
        ) from exc

    return AuthenticatedUser(user_id=user_id, username=x_username)
