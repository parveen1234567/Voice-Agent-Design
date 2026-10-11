from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BOLNA_API_BASE = "https://api.bolna.ai"
E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")


class BolnaError(RuntimeError):
    pass


def bolna_configuration() -> dict[str, bool]:
    return {
        "api_key": bool(os.environ.get("BOLNA_API_KEY")),
        "agent_id": bool(os.environ.get("BOLNA_AGENT_ID")),
        "admin_token": bool(os.environ.get("WEB_ADMIN_TOKEN")),
    }


def bolna_ready() -> bool:
    return all(bolna_configuration().values())


def validate_phone_number(phone_number: str) -> str:
    normalized = phone_number.strip()
    if not E164_PATTERN.fullmatch(normalized):
        raise ValueError("Enter the phone number in international E.164 format, for example +919876543210.")
    return normalized


def _bolna_request(path: str, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    api_key = os.environ.get("BOLNA_API_KEY")
    if not api_key:
        raise BolnaError("The server administrator has not configured BOLNA_API_KEY.")

    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(f"{BOLNA_API_BASE}{path}", data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=20) as response:
            response_data = response.read()
    except HTTPError as exc:
        detail = exc.read(2048).decode("utf-8", errors="replace")
        raise BolnaError(f"Bolna API returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise BolnaError(f"Could not connect to Bolna: {exc.reason}") from exc
    except TimeoutError as exc:
        raise BolnaError("Bolna did not respond before the request timed out.") from exc

    try:
        result = json.loads(response_data)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BolnaError("Bolna returned a response that was not valid JSON.") from exc
    if not isinstance(result, dict):
        raise BolnaError("Bolna returned an unexpected response format.")
    return result


def place_outbound_call(phone_number: str) -> dict[str, Any]:
    agent_id = os.environ.get("BOLNA_AGENT_ID")
    if not agent_id:
        raise BolnaError("The server administrator has not configured BOLNA_AGENT_ID.")
    recipient = validate_phone_number(phone_number)
    result = _bolna_request(
        "/call",
        "POST",
        {"agent_id": agent_id, "recipient_phone_number": recipient},
    )
    execution_id = result.get("execution_id")
    if not isinstance(execution_id, str) or not execution_id:
        raise BolnaError("Bolna did not return an execution ID for the call.")
    return {
        "execution_id": execution_id,
        "status": str(result.get("status", "queued")),
    }


def get_execution(execution_id: str) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9-]{8,100}", execution_id):
        raise ValueError("Invalid Bolna execution ID.")
    return _bolna_request(f"/executions/{execution_id}", "GET")
