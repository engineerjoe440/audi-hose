################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

import time
import secrets

import bcrypt
import jwt

JWT_SECRET = secrets.token_urlsafe(24) # Reloaded each time app starts
JWT_ALGORITHM ="HS256"
JWT_EXPIRY_LENGTH = 1800 # 30 minutes

def get_hashed_password(plain_text_password: str) -> str:
    """Hash a password for the first time."""
    # (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(
        plain_text_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode('utf-8')

def check_password(plain_text_password: str, hashed_password: str) -> bool:
    """Check hashed password."""
    # Using bcrypt the salt is saved into the hash itself
    return bcrypt.checkpw(
        plain_text_password.encode("utf-8"),
        hashed_password.encode("utf-8"))

def sign_jwt(payload: dict) -> dict[str, str]:
    """Generate a JSON Web Token (assuming valid authentication)."""
    payload["expires"] = time.time() + JWT_EXPIRY_LENGTH
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt(token: str) -> dict:
    """Decode the JSON Web Token and Validate it."""
    try:
        decoded_token = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        if decoded_token["expires"] >= time.time():
            return decoded_token
        else:
            return None
    except jwt.exceptions.DecodeError:
        return {}

def verify_token(token: str) -> bool:
    """Verify that the token can be decoded, and that it's valid."""
    try:
        payload = decode_jwt(token)
        return bool(payload)
    except jwt.exceptions.DecodeError:
        return False
