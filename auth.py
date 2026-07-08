import secrets
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

import config
import token_store


def build_authorize_url(state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": config.OURA_CLIENT_ID,
        "redirect_uri": config.OURA_REDIRECT_URI,
        "scope": config.OURA_SCOPES,
        "state": state,
    }
    return f"{config.OURA_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"


def exchange_code_for_tokens(code: str) -> dict:
    resp = requests.post(
        config.OURA_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": config.OURA_CLIENT_ID,
            "client_secret": config.OURA_CLIENT_SECRET,
            "redirect_uri": config.OURA_REDIRECT_URI,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        self.server.auth_code = params.get("code", [None])[0]
        self.server.auth_error = params.get("error", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Authorization complete. You can close this tab.</h2>")

    def log_message(self, *args):
        pass


def _capture_code_via_local_server(host: str, port: int) -> str:
    print(f"\nWaiting for redirect to {config.OURA_REDIRECT_URI} ...")

    server = HTTPServer((host, port), _CallbackHandler)
    server.auth_code = None
    server.auth_error = None
    server.handle_request()
    server.server_close()

    if not server.auth_code:
        raise SystemExit(f"Authorization failed: {server.auth_error or 'no code received'}")
    return server.auth_code


def _capture_code_via_manual_paste() -> str:
    print(
        "\nOURA_REDIRECT_URI is not localhost, so nothing on this machine is "
        "listening for the redirect. After you approve access, Oura will send "
        f"your browser to a URL starting with {config.OURA_REDIRECT_URI} — "
        "that page will likely fail to load, which is expected.\n"
        "Copy the full URL from your browser's address bar (or just the "
        "'code' value) and paste it below."
    )
    pasted = input("\nPaste the redirect URL (or the code): ").strip()

    if pasted.startswith("http"):
        query = urllib.parse.urlparse(pasted).query
        code = urllib.parse.parse_qs(query).get("code", [None])[0]
        if not code:
            raise SystemExit("No 'code' parameter found in the pasted URL.")
        return code

    return pasted


def run_oauth_setup() -> None:
    state = secrets.token_urlsafe(16)
    print("Open this URL in your browser to authorize:\n")
    print(build_authorize_url(state))

    parsed_redirect = urllib.parse.urlparse(config.OURA_REDIRECT_URI)
    if parsed_redirect.hostname in ("localhost", "127.0.0.1"):
        default_port = 443 if parsed_redirect.scheme == "https" else 80
        code = _capture_code_via_local_server(
            parsed_redirect.hostname, parsed_redirect.port or default_port
        )
    else:
        code = _capture_code_via_manual_paste()

    tokens = exchange_code_for_tokens(code)
    token_store.save_tokens(tokens)
    print(f"\nTokens saved to {config.TOKEN_FILE}")
