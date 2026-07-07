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


def run_oauth_setup() -> None:
    state = secrets.token_urlsafe(16)
    print("Open this URL in your browser to authorize:\n")
    print(build_authorize_url(state))
    print("\nWaiting for redirect to", config.OURA_REDIRECT_URI, "...")

    server = HTTPServer(("localhost", 8080), _CallbackHandler)
    server.auth_code = None
    server.auth_error = None
    server.handle_request()
    server.server_close()

    if not server.auth_code:
        raise SystemExit(f"Authorization failed: {server.auth_error or 'no code received'}")

    tokens = exchange_code_for_tokens(server.auth_code)
    token_store.save_tokens(tokens)
    print(f"\nTokens saved to {config.TOKEN_FILE}")
