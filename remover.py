import requests

SERVER = "https://school.probietech.com/parse"
APP_ID = "zjDlXWqwIv"

_HEADERS = {
    "X-Parse-Application-Id": APP_ID,
    "Content-Type": "application/json",
}


def login(username: str, password: str) -> tuple:
    """Returns (session_token, school_id)."""
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
    school_id = _extract_school_id(data)
    return token, school_id


def count_students(session_token: str, school_id: str) -> int:
    """Returns the current student count for the school (0 if class doesn't exist)."""
    resp = requests.get(
        f"{SERVER}/classes/Students_{school_id}",
        headers={**_HEADERS, "X-Parse-Session-Token": session_token},
        params={"limit": 0, "count": 1},
        timeout=15,
    )
    data = _json(resp)
    return int(data.get("count", 0))


def remove_all_students(session_token: str, school_id: str) -> dict:
    """
    Fetches student count first, then calls removeAllStudent cloud function.
    Returns dict with 'deleted' key containing the pre-deletion count.
    """
    before = count_students(session_token, school_id)

    resp = requests.post(
        f"{SERVER}/functions/removeAllStudent",
        json={"className": f"Students_{school_id}"},
        headers={**_HEADERS, "X-Parse-Session-Token": session_token},
        timeout=60,
    )
    data = _json(resp)
    if "error" in data:
        raise ValueError(data["error"])

    result = data.get("result", data)

    # If server returned a count use it, otherwise use pre-deletion count
    server_count = _extract_count(result)
    return {"deleted": server_count if server_count is not None else before}


def _extract_count(result) -> int | None:
    if isinstance(result, int):
        return result
    if isinstance(result, dict):
        for key in ("deleted", "removed", "count", "total", "studentDeleted",
                    "studentsDeleted", "deletedCount"):
            if key in result:
                try:
                    return int(result[key])
                except (TypeError, ValueError):
                    pass
        for v in result.values():
            try:
                return int(v)
            except (TypeError, ValueError):
                pass
    return None


def _extract_school_id(data: dict) -> str:
    field = data.get("schoolId")
    if isinstance(field, list) and field:
        entry = field[0]
        return entry.get("objectId", "") if isinstance(entry, dict) else ""
    if isinstance(field, dict):
        return field.get("objectId", "")
    return str(field or "")


def _json(resp) -> dict:
    text = resp.text.strip()
    if not text:
        raise ValueError(f"Empty response (HTTP {resp.status_code}).")
    try:
        return resp.json()
    except Exception:
        raise ValueError(f"Non-JSON response (HTTP {resp.status_code}): {text[:200]}")
