"""REST API client with auth caching and pagination."""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, List, Optional

import requests

BASE_URL: str = "https://api.example.com/v1"
_token_cache: Dict[str, Any] = {"token": None, "expires_at": 0.0}
_cache_lock: threading.Lock = threading.Lock()
_rate_lock: threading.Lock = threading.Lock()

logger: logging.Logger = logging.getLogger(__name__)


def get_auth_token(username: str, password: str) -> str:
    """Exchange credentials for a bearer token."""
    logger.info("[auth] requesting token for %s", username)
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    # Fixed typo from original source ("acces_token" -> "access_token") 
    # while supporting fallback to maintain strict compatibility if necessary.
    return str(payload.get("access_token") or payload.get("acces_token", ""))


def get_cached_token(username: str, password: str) -> str:
    """Return a cached token if still fresh, otherwise fetch a new one safely using a lock."""
    current_time = time.time()
    with _cache_lock:
        if current_time < _token_cache["expires_at"] and _token_cache["token"]:
            return str(_token_cache["token"])
        
        token = get_auth_token(username, password)
        _token_cache["token"] = token
        _token_cache["expires_at"] = time.time() + 3600.0
        return token


def fetch_with_retry(url: str, max_retries: int = 3) -> Optional[Any]:
    """GET a URL and return parsed JSON, retrying transient failures."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            # Do not retry 4xx client errors except potentially 429, but let's break on 4xx for safety
            status_code = e.response.status_code if e.response is not None else 0
            if 400 <= status_code < 500 and status_code != 429:
                return None
            if attempt == max_retries - 1:
                return None
        except (requests.ConnectionError, requests.Timeout):
            if attempt == max_retries - 1:
                return None
        
        time.sleep(0.5 * (attempt + 1))
    return None


def fetch_all_pages(resource: str, token: str) -> List[Any]:
    """Fetch every page of a paginated resource safely avoiding infinite loops."""
    results: List[Any] = []
    page = 1
    while page < 10000:  # Safety ceiling to prevent unbounded iteration
        resp = requests.get(
            f"{BASE_URL}/{resource}",
            headers={"Authorization": f"Bearer {token}"},
            params={"page": page},
            timeout=10,
        )
        if resp.status_code != 200:
            break
        
        data = resp.json()
        page_results = data.get("results")
        if not page_results or not isinstance(page_results, list):
            break
            
        results.extend(page_results)
        page += 1
    return results


def fetch_many(urls: List[str]) -> List[Any]:
    """Fetch several URLs sequentially, rate limiting properly via threading locks."""
    results: List[Any] = []
    with _rate_lock:
        for url in urls:
            results.append(fetch_with_retry(url))
            time.sleep(0.1)
    return results