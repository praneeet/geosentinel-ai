import base64
import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

# Pre-seeded demo user registry with SHA-256 password digests
DEMO_USERS: Dict[str, Dict[str, Any]] = {
    "admin": {
        "username": "admin",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "full_name": "Chief Information Security Officer (CISO)",
        "role": "ADMINISTRATOR",
        "permissions": ["read", "simulate", "copilot", "dossier", "ingest", "diagnostics"],
    },
    "analyst": {
        "username": "analyst",
        "password_hash": hashlib.sha256("analyst123".encode()).hexdigest(),
        "full_name": "Senior Geopolitical Risk Analyst",
        "role": "SENIOR_ANALYST",
        "permissions": ["read", "simulate", "copilot", "dossier"],
    },
    "officer": {
        "username": "officer",
        "password_hash": hashlib.sha256("officer123".encode()).hexdigest(),
        "full_name": "Tactical Operations Watch Officer",
        "role": "WATCH_OFFICER",
        "permissions": ["read", "copilot"],
    },
}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    full_name: str
    permissions: List[str]

class UserProfile(BaseModel):
    username: str
    full_name: str
    role: str
    permissions: List[str]

def create_jwt_token(payload: dict, expires_in_seconds: int = 86400) -> str:
    """Cryptographically signed HMAC-SHA256 JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload_copy = dict(payload)
    payload_copy["exp"] = int(time.time()) + expires_in_seconds

    hdr_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    pay_b64 = base64.urlsafe_b64encode(json.dumps(payload_copy).encode()).decode().rstrip("=")
    msg = f"{hdr_b64}.{pay_b64}"

    sig = hmac.new(settings.SECRET_KEY.encode(), msg.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{msg}.{sig_b64}"

def verify_jwt_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        msg = f"{parts[0]}.{parts[1]}"
        expected_sig = hmac.new(settings.SECRET_KEY.encode(), msg.encode(), hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(parts[2] + "==")
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload_json = base64.urlsafe_b64decode(parts[1] + "==").decode()
        payload = json.loads(payload_json)
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    if not token:
        # In strict production mode without demo mode enabled, require valid bearer token
        if settings.ENVIRONMENT == "production" and not settings.DEMO_MODE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials were not provided",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Default fallback to administrator for local demo / development convenience
        return DEMO_USERS["admin"]
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    username = payload.get("sub")
    user = DEMO_USERS.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

def require_permission(permission: str):
    """Enforces specific RBAC permission requirement on protected endpoints."""
    async def _check_perm(current_user: dict = Depends(get_current_user)) -> dict:
        user_perms = current_user.get("permissions", [])
        user_role = current_user.get("role", "")
        if user_role != "ADMINISTRATOR" and permission not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Security policy requires '{permission}' permission",
            )
        return current_user
    return _check_perm

def require_role(roles: List[str]):
    """Enforces minimum RBAC role requirement on protected endpoints."""
    async def _check_role(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "")
        if user_role not in roles and user_role != "ADMINISTRATOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation restricted to roles: {', '.join(roles)}",
            )
        return current_user
    return _check_role

@router.post("/auth/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates intelligence analysts and issues a cryptographically signed JWT token.
    Pre-seeded demo accounts:
    - admin / admin123 (ADMINISTRATOR)
    - analyst / analyst123 (SENIOR_ANALYST)
    - officer / officer123 (WATCH_OFFICER)
    """
    user = DEMO_USERS.get(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    entered_hash = hashlib.sha256(form_data.password.encode()).hexdigest()
    if not hmac.compare_digest(user["password_hash"], entered_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_jwt_token({
        "sub": user["username"],
        "role": user["role"],
        "name": user["full_name"],
    })
    return TokenResponse(
        access_token=token,
        role=user["role"],
        username=user["username"],
        full_name=user["full_name"],
        permissions=user["permissions"],
    )

@router.get("/auth/me", response_model=UserProfile)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Returns the authenticated analyst's operational profile and RBAC permissions."""
    return UserProfile(
        username=current_user["username"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        permissions=current_user["permissions"],
    )

@router.get("/auth/roles")
async def list_available_roles():
    """Lists role definitions and access tiers."""
    return [
        {
            "role": "ADMINISTRATOR",
            "title": "System Administrator",
            "description": "Full administrative control, manual ingestion triggers, and observability diagnostics.",
        },
        {
            "role": "SENIOR_ANALYST",
            "title": "Senior Intelligence Analyst",
            "description": "Execute What-If scenario simulations, query AI Copilot, and export strategic intelligence dossiers.",
        },
        {
            "role": "WATCH_OFFICER",
            "title": "Tactical Watch Officer",
            "description": "Situational awareness monitoring of choropleth map, real-time news wire, and incoming alerts.",
        },
    ]

