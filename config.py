import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing {name}. Copy .env.example to .env and fill it in.")
    return value


OURA_CLIENT_ID = _require("OURA_CLIENT_ID")
OURA_CLIENT_SECRET = _require("OURA_CLIENT_SECRET")
OURA_REDIRECT_URI = os.environ.get("OURA_REDIRECT_URI", "http://localhost:8080/callback")

ROUTINE_TRIGGER_URL = _require("ROUTINE_TRIGGER_URL")
ROUTINE_API_TOKEN = _require("ROUTINE_API_TOKEN")

TOKEN_FILE = BASE_DIR / "tokens.json"

OURA_AUTHORIZE_URL = "https://cloud.ouraring.com/oauth/authorize"
OURA_TOKEN_URL = "https://api.ouraring.com/oauth/token"
OURA_API_BASE = "https://api.ouraring.com/v2/usercollection"

OURA_SCOPES = os.environ.get(
    "OURA_SCOPES",
    "email personal daily heartrate workout tag session spo2 stress heart_health",
)
