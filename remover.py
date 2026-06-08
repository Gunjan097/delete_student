import requests

SERVER = "https://school.probietech.com/parse"
APP_ID = "zjDlXWqwIv"

_HEADERS = {
    "X-Parse-Application-Id": APP_ID,
    "Content-Type": "application/json",
}


def login(username: str, password: str) -> str:
    resp = requests.post(
        f"{SERVER}/login",
        json={"username": username, "password": password},
        headers=_HEADERS,
        timeout=15,
    )
    data = _json(resp)
    if "error" in data:
        raise ValueError(data["error"])
    token = data.get("sessionToken", "")
    if not token:
        raise ValueError("No session token received.")
    return token


def remove_all_students(session_token: str) -> dict:
    """
    Calls the removeAllStudent cloud function.
    Returns the raw result dict from the server.
    """
    resp = requests.post(
        f"{SERVER}/functions/removeAllStudent",
        json={},
        headers={**_HEADERS, "X-Parse-Session-Token": session_token},
        timeout=60,
    )
    data = _json(resp)
    if "error" in data:
        raise ValueError(data["error"])
    return data.get("result", data)


def _json(resp) -> dict:
    text = resp.text.strip()
    if not text:
        raise ValueError(f"Empty response (HTTP {resp.status_code}).")
    try:
        return resp.json()
    except Exception:
        raise ValueError(f"Non-JSON response (HTTP {resp.status_code}): {text[:200]}")
