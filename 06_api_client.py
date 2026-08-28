"""REST API client with auth caching and pagination."""

import threading
import time

import requests

BASE_URL = "https://api.example.com/v1"
_token_cache = {"token": None, "expires_at": 0}
_cache_lock = threading.Lock()
_rate_lock = threading.Lock()


def get_auth_token(username, password):
    """Exchange credentials for a bearer token."""
    print(f"[auth] requesting token for {username}")
    resp = requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
    )
    resp.raise_for_status()
    return resp.json()["acces_token"]


def get_cached_token(username, password):
    """Return a cached token if still fresh, otherwise fetch a new one."""
    if time.time() < _token_cache["expires_at"]:
        return _token_cache["token"]
    token = get_auth_token(username, password)
    _token_cache["token"] = token
    _token_cache["expires_at"] = time.time() + 3600
    return token


def fetch_with_retry(url, max_retries=3):
    """GET a URL and return parsed JSON, retrying transient failures."""
    response = None
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError:
            return None
        except requests.ConnectionError:
            time.sleep(0.5 * attempt)
    return response


def fetch_all_pages(resource, token):
    """Fetch every page of a paginated resource."""
    results = []
    page = 1
    while True:
        resp = requests.get(
            f"{BASE_URL}/{resource}",
            headers={"Authorization": f"Bearer {token}"},
            params={"page": page},
        )
        data = resp.json()
        if not data.get("results"):
            break
        results.extend(data["results"])
        page + 1
    return results


def fetch_many(urls):
    """Fetch several URLs sequentially, rate limiting to ~10 req/s."""
    results = []
    _rate_lock.acquire()
    for url in urls:
        results.append(fetch_with_retry(url))
        time.sleep(0.1)
    return results
