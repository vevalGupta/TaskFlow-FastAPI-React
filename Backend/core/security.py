# security.py
# Two responsibilities:
#   1. Hash and verify passwords with bcrypt
#   2. Create and decode JWT access + refresh tokens

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from Backend.core.config import settings

# passlib handles bcrypt — rounds controls how slow the hash is (12 is a good default)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


# ── Passwords ─────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Turn a plain-text password into a bcrypt hash."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored hash."""
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ───────────────────────────────────────────────

def _make_token(payload: dict, expires: timedelta, secret: str) -> str:
    """Internal helper — adds exp/iat and signs the token."""
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + expires
    data["iat"] = datetime.now(timezone.utc)
    return jwt.encode(data, secret, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str, role: str) -> str:
    """Short-lived token (15 min). Carries user id + role."""
    return _make_token(
        {"sub": user_id, "role": role, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        settings.JWT_SECRET,
    )


def create_refresh_token(user_id: str) -> str:
    """Long-lived token (7 days). Used only to get a new access token."""
    # Different secret so a leaked access token can't be used as a refresh token
    return _make_token(
        {"sub": user_id, "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        settings.JWT_SECRET + "_refresh",
    )


def decode_access_token(token: str) -> dict:
    """
    Decode and validate an access token.
    Raises ValueError with a short code string on failure.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise ValueError("TOKEN_INVALID")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("TOKEN_EXPIRED")
    except JWTError:
        raise ValueError("TOKEN_INVALID")


def decode_refresh_token(token: str) -> dict:
    """Decode and validate a refresh token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET + "_refresh",
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise ValueError("REFRESH_TOKEN_INVALID")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("REFRESH_TOKEN_EXPIRED")
    except JWTError:
        raise ValueError("REFRESH_TOKEN_INVALID")