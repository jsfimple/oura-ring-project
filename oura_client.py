from datetime import date

import requests

import config
import token_store

ENDPOINTS_DATE = [
    "daily_sleep",
    "sleep",
    "sleep_time",
    "daily_readiness",
    "daily_activity",
    "daily_spo2",
    "daily_stress",
    "daily_resilience",
    "daily_cardiovascular_age",
    "vO2_max",
    "workout",
    "session",
    "tag",
    "enhanced_tag",
]

ENDPOINTS_DATETIME = ["heartrate"]

# Output key to use for endpoints whose URL slug isn't a clean dict key.
OUTPUT_KEY_OVERRIDES = {"vO2_max": "vo2_max"}


def refresh_access_token(refresh_token: str) -> dict:
    resp = requests.post(
        config.OURA_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": config.OURA_CLIENT_ID,
            "client_secret": config.OURA_CLIENT_SECRET,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return token_store.save_tokens(resp.json())


def ensure_valid_access_token() -> str:
    tokens = token_store.load_tokens()
    if tokens is None:
        raise SystemExit("No saved tokens found. Run: python main.py auth")

    if token_store.is_expired(tokens):
        tokens = refresh_access_token(tokens["refresh_token"])

    return tokens["access_token"]


def _safe_get(slug: str, headers: dict, params: dict) -> dict:
    try:
        resp = requests.get(f"{config.OURA_API_BASE}/{slug}", headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        status_code = getattr(exc.response, "status_code", None)
        return {"error": str(exc), "status_code": status_code}


def fetch_all(access_token: str, target_date: date | None = None) -> dict:
    target_date = target_date or date.today()
    headers = {"Authorization": f"Bearer {access_token}"}
    date_str = target_date.isoformat()

    bundle: dict = {}

    for slug in ENDPOINTS_DATE:
        key = OUTPUT_KEY_OVERRIDES.get(slug, slug)
        bundle[key] = _safe_get(slug, headers, {"start_date": date_str, "end_date": date_str})

    for slug in ENDPOINTS_DATETIME:
        bundle[slug] = _safe_get(
            slug,
            headers,
            {"start_datetime": f"{date_str}T00:00:00", "end_datetime": f"{date_str}T23:59:59"},
        )

    bundle["_meta"] = {"target_date": date_str}

    return bundle
