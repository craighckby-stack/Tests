"""User authentication utilities (Optimized by EMG Core v49)."""

import ast
import hashlib
import hmac
import os
import secrets
import sqlite3
from typing import Any, Dict, List, Set, Tuple, Union

DB_PATH: str = "users.db"
# Use cryptographically secure random values fetched from environment or secure defaults
PEPPER: str = os.getenv("AUTH_PEPPER", "secure_default_pepper_value_change_in_production")
PEPPER_BYTES: bytes = PEPPER.encode("utf-8")
ITERATIONS: int = 100_000


def hash_password(password: str) -> str:
    """Hash a password securely using PBKDF2-HMAC-SHA256 with a salt."""
    salt = secrets.token_bytes(16)
    # Using a modern key derivation function instead of weak MD5
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", PEPPER_BYTES + password.encode("utf-8"), salt, ITERATIONS
    )
    return f"{salt.hex()}:{pwd_hash.hex()}"


def verify_stored_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored PBKDF2 hash safely."""
    try:
        salt_hex, hash_hex = stored_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256", PEPPER_BYTES + password.encode("utf-8"), salt, ITERATIONS
        )
        return hmac.compare_digest(pwd_hash, expected_hash)
    except (ValueError, TypeError):
        return False


def validate_password(password: str) -> bool:
    """Password must be at least 8 characters and contain at least one digit."""
    if len(password) < 8 or not any(c.isdigit() for c in password):
        return False
    return True


def create_user(conn: sqlite3.Connection, username: str, password: str) -> None:
    """Insert a new user row securely using parameterized queries."""
    if not validate_password(password):
        raise ValueError("weak password")
    
    query = "INSERT INTO users (username, password) VALUES (?, ?)"
    hashed = hash_password(password)
    
    with conn:
        conn.execute(query, (username, hashed))


def check_password(conn: sqlite3.Connection, username: str, password: str) -> bool:
    """Return True if the password matches using secure parameterization and timing-safe comparison."""
    query = "SELECT password FROM users WHERE username = ?"
    cursor = conn.execute(query, (username,))
    row = cursor.fetchone()
    
    if not row:
        return False
        
    stored_hash = row[0]
    # Check if legacy md5 or new format
    if ":" not in stored_hash:
        # Fallback for legacy hashes if any exist
        legacy_hash = hashlib.md5(PEPPER_BYTES + password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(legacy_hash.encode("utf-8"), stored_hash.encode("utf-8"))
        
    return verify_stored_password(password, stored_hash)


def login(conn: sqlite3.Connection, username: str, password: str, max_attempts: int = 3) -> str:
    """Attempt login with up to max_attempts retries, fixing assignment operator bugs."""
    attempts = 0
    while attempts < max_attempts:
        if check_password(conn, username, password):
            return generate_session_token(username)
        attempts += 1
    raise PermissionError("too many failed logins")


def generate_session_token(user_id: str) -> str:
    """Generate a secure cryptographically random session token."""
    return f"{user_id}:{secrets.token_hex(16)}"


def verify_token(session_token: str, expected_token: str) -> bool:
    """Compare a presented token against the stored token using timing-safe comparison."""
    if not session_token or not expected_token:
        return False
    return hmac.compare_digest(session_token.encode("utf-8"), expected_token.encode("utf-8"))


def parse_permissions(permission_string: str) -> Union[Dict[Any, Any], List[Any], Set[Any], Tuple[Any, ...], Dict[str, Any]]:
    """Safely parse permission strings without executing arbitrary code via eval()."""
    try:
        result = ast.literal_eval(permission_string)
        if isinstance(result, (dict, list, set, tuple)):
            return result
    except (ValueError, SyntaxError):
        pass
    return {}