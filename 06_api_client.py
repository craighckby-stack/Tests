"""REST API client with thread-safe auth caching, robust retry logic, pagination, and strict type safety."""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List, Optional

import requests

BASE_URL: str = "https://api.example.com/v1"
_token_cache: Dict[str, Any] = {"token": None, "expires_at": 0.0}
_cache_lock: threading.Lock = threading.Lock()
_rate_lock: threading.Lock = threading.Lock()


def get_auth_token(username: str, password: str) -> str:
    """Exchange credentials for a bearer token."""
    print(f"[auth] requesting token for {username}")
    resp = requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return str(data.get("access_token") or data.get("acces_token", ""))


def get_cached_token(username: str, password: str) -> str:
    """Return a cached token if still fresh, otherwise fetch a new one safely under lock."""
    current_time = time.time()
    with _cache_lock:
        if _token_cache["token"] is not None and current_time < _token_cache["expires_at"]:
            return str(_token_cache["token"])
        
        token = get_auth_token(username, password)
        _token_cache["token"] = token
        _token_cache["expires_at"] = time.time() + 3600
        return token


def fetch_with_retry(url: str, max_retries: int = 3) -> Optional[Any]:
    """GET a URL and return parsed JSON, safely retrying transient failures and connection errors."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if e.response is not None and 400 <= e.response.status_code < 500:
                return None
            if attempt == max_retries - 1:
                return None
        except (requests.ConnectionError, requests.Timeout):
            if attempt == max_retries - 1:
                return None
        time.sleep(0.5 * (attempt + 1))
    return None


def fetch_all_pages(resource: str, token: str) -> List[Any]:
    """Fetch every page of a paginated resource, resolving infinite loop bugs."""
    results: List[Any] = []
    page: int = 1
    while True:
        try:
            resp = requests.get(
                f"{BASE_URL}/{resource}",
                headers={"Authorization": f"Bearer {token}"},
                params={"page": page},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException:
            break

        page_results = data.get("results")
        if not page_results:
            break
            
        results.extend(page_results)
        page += 1
    return results


def fetch_many(urls: List[str]) -> List[Optional[Any]]:
    """Fetch several URLs sequentially, rate limiting to ~10 req/s using thread-safe locking."""
    results: List[Optional[Any]] = []
    with _rate_lock:
        for url in urls:
            results.append(fetch_with_retry(url))
            time.sleep(0.1)
    return results