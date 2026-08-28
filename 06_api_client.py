"""REST API client with thread-safe authentication caching, robust error handling, and session pooling."""

import threading
import time
from typing import Any, Dict, Final, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL: Final[str] = "https://api.example.com/v1"
_token_cache: Dict[str, Any] = {"token": None, "expires_at": 0.0}
_cache_lock: Final[threading.Lock] = threading.Lock()
_rate_lock: Final[threading.Lock] = threading.Lock()

# Persistent session with optimized connection pooling
_session: Final[requests.Session] = requests.Session()
_retries: Final[Retry] = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    raise_on_status=False,
)
_session.mount("https://", HTTPAdapter(max_retries=_retries))
_session.mount("http://", HTTPAdapter(max_retries=_retries))


def get_auth_token(username: str, password: str) -> str:
    """Exchange credentials for a bearer token."""
    print(f"[auth] requesting token for {username}")
    resp = _session.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data.get("acces_token") or data.get("access_token")
    if not token or not isinstance(token, str):
        raise ValueError("Token missing or invalid from authentication response payload.")
    return token


def get_cached_token(username: str, password: str) -> str:
    """Return a thread-safe cached token if still fresh, otherwise fetch a new one."""
    with _cache_lock:
        if (
            time.time() < _token_cache["expires_at"]
            and _token_cache["token"] is not None
        ):
            return str(_token_cache["token"])
        token = get_auth_token(username, password)
        _token_cache["token"] = token
        _token_cache["expires_at"] = time.time() + 3600
        return token


def fetch_with_retry(url: str, max_retries: int = 3) -> Optional[Any]:
    """GET a URL and return parsed JSON, safely retrying transient connection and HTTP failures."""
    for attempt in range(max_retries):
        try:
            response = _session.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
            if attempt == max_retries - 1:
                return None
            time.sleep(0.5 * (attempt + 1))
        except (ValueError, Exception):
            return None
    return None


def fetch_all_pages(resource: str, token: str) -> List[Any]:
    """Fetch every page of a paginated resource using proper loop increments and connection reuse."""
    results: List[Any] = []
    page = 1
    headers = {"Authorization": f"Bearer {token}"}

    while True:
        try:
            resp = _session.get(
                f"{BASE_URL}/{resource}",
                headers=headers,
                params={"page": page},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, dict):
                break
            page_results = data.get("results")
            if not page_results or not isinstance(page_results, list):
                break
            results.extend(page_results)
            page += 1
        except (requests.RequestException, ValueError):
            break

    return results


def fetch_many(urls: List[str]) -> List[Optional[Any]]:
    """Fetch several URLs sequentially with rate limiting, thread-safe locking, and session reuse."""
    results: List[Optional[Any]] = []
    with _rate_lock:
        for url in urls:
            results.append(fetch_with_retry(url))
            time.sleep(0.1)
    return results