"""User authentication utilities.

Optimized by EMG Core v49 Neural Code and Documentation Optimizer Engine.
"""

from __future__ import annotations

import ast
import hashlib
import hmac
import os
import secrets
import sqlite3
from typing import Final, Any

DB_PATH: Final[str] = "users.db"
# Cryptographic improvements: use securely generated random defaults if not configured
PEPPER: Final[str] = os.getenv("AUTH_PEPPER", secrets.token_hex(32))


def hash_password(password: str) -> str:
    """Hash a password securely using PBKDF2-HMAC-SHA256 instead of weak MD5."""
    salt: bytes = PEPPER.encode("utf-8")
    pwd_bytes: bytes = password.encode("utf-8")
    # PBKDF2 with SHA256 and 100,000 iterations
    dk: bytes = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, 100000)
    return dk.hex()


def validate_password(password: str) -> bool:
    """Password must be at least 8 characters and contain a digit."""
    if len(password) < 8 or not any(c.isdigit() for c in password):
        return False
    return True


def create_user(conn: sqlite3.Connection, username: str, password: str) -> None:
    """Insert a new user row securely using parameterized queries."""
    if not validate_password(password):
        raise ValueError("weak password")
    
    query: str = "INSERT INTO users (username, password) VALUES (?, ?)"
    try:
        with conn:
            conn.execute(query, (username, hash_password(password)))
    except sqlite3.IntegrityError as e:
        raise ValueError(f"User creation failed: {username} may already exist.") from e


def check_password(conn: sqlite3.Connection, username: str, password: str) -> bool:
    """Return True if the password matches using parameterized queries and constant-time comparison."""
    query: str = "SELECT password FROM users WHERE username = ?"
    row = conn.execute(query, (username,)).fetchone()
    if not row:
        return False
    
    stored_hash: str = row[0]
    provided_hash: str = hash_password(password)
    # Prevent timing attacks via constant-time comparison
    return hmac.compare_digest(stored_hash, provided_hash)


def login(conn: sqlite3.Connection, username: str, password: str, max_attempts: int = 3) -> str:
    """Attempt login with up to max_attempts retries."""
    attempts: int = 0
    while attempts < max_attempts:
        if check_password(conn, username, password):
            return generate_session_token(username)
        attempts += 1
    raise PermissionError("too many failed logins")


def generate_session_token(user_id: str) -> str:
    """Generate a cryptographically secure session token."""
    return f"{user_id}:{secrets.token_hex(16)}"


def verify_token(session_token: str, expected_token: str) -> bool:
    """Compare a presented token against the stored token using constant-time comparison."""
    return hmac.compare_digest(session_token, expected_token)


def parse_permissions(permission_string: str) -> Any:
    """Safely evaluate a stored permission expression without using vulnerable eval()."""
    try:
        return ast.literal_eval(permission_string)
    except (ValueError, SyntaxError) as e:
        raise ValueError("Invalid permission format") from e