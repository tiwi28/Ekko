"""Signup, login, and "who am I"."""

from fastapi import APIRouter, Depends, status
from psycopg import Connection

from app.config import Settings, get_settings
from app.db import get_conn
from app.schemas import LoginRequest, SignupRequest, TokenResponse, UserOut
from app.security import get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
    body: SignupRequest,
    conn: Connection = Depends(get_conn),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """Create a user and return a JWT.

    TODO:
      - lowercase the email (the DB has a CHECK that enforces this)
      - hash the password with security.hash_password
      - SQL: insert the user and return its id
      - catch psycopg.errors.UniqueViolation -> 409 "email already registered"
      - return TokenResponse(access_token=create_access_token(user_id, settings))
    """
    raise NotImplementedError("signup")


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    conn: Connection = Depends(get_conn),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """Check credentials and return a JWT.

    TODO:
      - SQL: look up id + password_hash by (lowercased) email
      - if no row or security.verify_password fails -> 401 (same message for both)
      - return a token
    """
    raise NotImplementedError("login")


@router.get("/me", response_model=UserOut)
def me(
    user_id: int = Depends(get_current_user_id),
    conn: Connection = Depends(get_conn),
) -> UserOut:
    """Return the logged-in user's profile.

    TODO:
      - SQL: select id, email, created_at for user_id
      - 404 if the user was deleted after the token was issued
    """
    raise NotImplementedError("me")
