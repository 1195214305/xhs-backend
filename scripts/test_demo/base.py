"""
Base utilities for test demo modules
"""
import urllib.request
import json

BASE_URL = "http://localhost:3005"


def make_get_request(endpoint: str, timeout: int = 10) -> dict:
    """Make a GET request and return parsed JSON"""
    req = urllib.request.Request(f"{BASE_URL}{endpoint}")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def make_post_request(endpoint: str, payload: dict, timeout: int = 15) -> dict:
    """Make a POST request with JSON payload and return parsed JSON"""
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def print_success(msg: str):
    print(f"    ✅ {msg}")


def print_warning(msg: str):
    print(f"    ⚠️ {msg}")


def print_error(msg: str):
    print(f"    ❌ {msg}")
