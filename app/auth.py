import os
import logging
from typing import Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import jwt
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

from app.database import supabase, SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger("pathforge.auth")
security = HTTPBearer(auto_error=False)

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")


class AuthenticatedUser(BaseModel):
    id: str
    email: Optional[str] = None
    access_token: str


def get_user_supabase_client(access_token: str) -> Client:
    """
    Returns a Supabase client scoped to the authenticated user's JWT.
    This guarantees that PostgREST and Supabase Storage operations
    execute under the user's RLS policies.
    """
    client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    if access_token:
        client.postgrest.auth(access_token)
        try:
            client.storage._headers["Authorization"] = f"Bearer {access_token}"
        except Exception:
            pass
    return client


def ensure_user_profile(user_id: str, email: Optional[str], access_token: str) -> None:
    """
    Ensures a corresponding record exists in public.profiles.
    The public.resumes table has a foreign key constraint referencing profiles.id.
    """
    try:
        user_client = get_user_supabase_client(access_token)
        # Check if profile already exists
        existing = user_client.table("profiles").select("id").eq("id", user_id).execute()
        if not existing.data:
            user_client.table("profiles").insert({
                "id": user_id,
                "email": email or "",
                "full_name": email.split("@")[0] if email else "User"
            }).execute()
    except Exception as exc:
        # If already exists or insert fails, log but don't disrupt auth flow
        logger.debug(f"Profile check/insert result for user {user_id}: {exc}")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> AuthenticatedUser:
    """
    FastAPI dependency that extracts and validates the Supabase JWT.
    Never trusts client-supplied user IDs; verifies the token signature
    and extracts the verified user identity from Supabase Auth.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization bearer token. Please log in to continue.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()

    # 1. Attempt token verification via Supabase Auth API
    try:
        user_response = supabase.auth.get_user(token)
        if user_response and user_response.user:
            user = user_response.user
            user_id = str(user.id)
            email = user.email

            # Ensure profile exists for foreign key integrity
            ensure_user_profile(user_id, email, token)

            return AuthenticatedUser(
                id=user_id,
                email=email,
                access_token=token
            )
    except Exception as api_err:
        logger.debug(f"Supabase auth.get_user verification failed: {api_err}")

    # 2. Fallback: Local PyJWT verification if SUPABASE_JWT_SECRET is configured
    if SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload: missing subject identifier.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            email = payload.get("email")
            ensure_user_profile(user_id, email, token)

            return AuthenticatedUser(
                id=str(user_id),
                email=email,
                access_token=token
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.PyJWTError as jwt_err:
            logger.warning(f"PyJWT decode error: {jwt_err}")

    # If verification reached here, token is invalid or expired
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token. Please re-authenticate.",
        headers={"WWW-Authenticate": "Bearer"},
    )
