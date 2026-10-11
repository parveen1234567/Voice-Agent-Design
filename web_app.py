from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import os
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse
from uuid import uuid4

from voice_agent.conversation import AgentState, get_next_question, handle_customer_utterance
from voice_agent.bolna_client import (
    BolnaError,
    bolna_ready,
    get_execution,
    place_outbound_call,
)


ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
MAX_REQUEST_BYTES = 16_384
SESSIONS: dict[str, AgentState] = {}
SESSIONS_LOCK = Lock()
TERMINAL_STATUSES = {"callback", "transfer", "disqualified", "ended", "complete"}


class RequestError(ValueError):
    pass


class VoiceAgentDemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
        elif path == "/api/health":
            self._send_json(200, {"status": "ok"})
        elif path == "/api/bolna/status":
            self._send_json(200, {"configured": bolna_ready()})
        elif path.startswith("/api/bolna/executions/"):
            self._get_bolna_execution(path.rsplit("/", 1)[-1], {})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._read_json()
            if path == "/api/session":
                self._create_session(body)
            elif path == "/api/message":
                self._send_message(body)
            elif path == "/api/bolna/calls":
                self._place_bolna_call(body)
            elif path.startswith("/api/bolna/executions/"):
                execution_id = path.rsplit("/", 1)[-1]
                self._get_bolna_execution(execution_id, body)
            else:
                self._send_json(404, {"error": "Not found"})
        except RequestError as exc:
            self._send_json(400, {"error": str(exc)})

    def _is_authorized(self, body: dict) -> bool:
        configured_token = os.environ.get("WEB_ADMIN_TOKEN")
        request_token = self.headers.get("X-Demo-Admin-Token", "")
        body_token = body.get("admin_token", "")
        if not isinstance(body_token, str):
            body_token = ""
        return bool(
            configured_token
            and (
                hmac.compare_digest(request_token, configured_token)
                or hmac.compare_digest(body_token, configured_token)
            )
        )

    def _place_bolna_call(self, body: dict) -> None:
        if not self._is_authorized(body):
            self._send_json(401, {"error": "Outbound calling is not authorized. Check the call-admin token."})
            return
        if not bolna_ready():
            self._send_json(503, {"error": "Bolna is not configured. Set BOLNA_API_KEY, BOLNA_AGENT_ID, and WEB_ADMIN_TOKEN."})
            return
        phone_number = body.get("phone_number")
        if not isinstance(phone_number, str):
            raise RequestError("phone_number is required")
        if body.get("confirm_cost_and_consent") is not True:
            raise RequestError("Confirm that you are authorized to call this number and understand the call may incur charges.")
        try:
            result = place_outbound_call(phone_number)
        except ValueError as exc:
            raise RequestError(str(exc)) from exc
        except BolnaError as exc:
            self._send_json(502, {"error": str(exc)})
            return
        self._send_json(202, result)

    def _get_bolna_execution(self, execution_id: str, body: dict) -> None:
        if not self._is_authorized(body):
            self._send_json(401, {"error": "Call status is not authorized. Check the call-admin token."})
            return
        if not bolna_ready():
            self._send_json(503, {"error": "Bolna is not configured on this server."})
            return
        try:
            result = get_execution(execution_id)
        except ValueError as exc:
            raise RequestError(str(exc)) from exc
        except BolnaError as exc:
            self._send_json(502, {"error": str(exc)})
            return
        # Return only call outcome fields; do not expose provider-side data unnecessarily.
        telephony_data = result.get("telephony_data")
        self._send_json(
            200,
            {
                "execution_id": result.get("id", execution_id),
                "status": result.get("status", "unknown"),
                "transcript": result.get("transcript"),
                "recording_url": (
                    telephony_data.get("recording_url")
                    if isinstance(telephony_data, dict)
                    else None
                ),
                "duration_seconds": result.get("conversation_duration"),
            },
        )

    def _read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise RequestError("Invalid Content-Length header") from exc
        if length <= 0 or length > MAX_REQUEST_BYTES:
            raise RequestError("Request body must be between 1 byte and 16 KB")
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RequestError("Request body must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise RequestError("Request body must be a JSON object")
        return payload

    def _create_session(self, body: dict) -> None:
        name = body.get("customer_name", "Rahul")
        if not isinstance(name, str) or not name.strip() or len(name) > 80:
            raise RequestError("Enter a customer name between 1 and 80 characters")
        session_id = uuid4().hex
        state = AgentState(customer_name=name.strip())
        with SESSIONS_LOCK:
            SESSIONS[session_id] = state
        self._send_json(
            201,
            {
                "session_id": session_id,
                "assistant_message": get_next_question(state),
                "done": False,
            },
        )

    def _send_message(self, body: dict) -> None:
        session_id = body.get("session_id")
        message = body.get("message")
        if not isinstance(session_id, str) or not isinstance(message, str) or not message.strip():
            raise RequestError("Both session_id and a non-empty message are required")
        with SESSIONS_LOCK:
            state = SESSIONS.get(session_id)
            if state is None:
                self._send_json(404, {"error": "Session not found. Start a new demo."})
                return
            result = handle_customer_utterance(state, message.strip())
            next_question = result.get("next_question")
            messages = [result["response"]]
            if next_question and next_question != result["response"]:
                messages.append(next_question)
            self._send_json(
                200,
                {
                    "assistant_messages": messages,
                    "status": result["status"],
                    "done": result["status"] in TERMINAL_STATUSES,
                },
            )

    def _send_file(self, path: Path, content_type: str) -> None:
        try:
            content = path.read_bytes()
        except OSError:
            self._send_json(500, {"error": "The web interface could not be loaded"})
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, status: int, body: dict) -> None:
        content = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), VoiceAgentDemoHandler)
    print(f"Voice agent demo available on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
