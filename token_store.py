import json
import os
import time

import config


def load_tokens() -> dict | None:
    if not config.TOKEN_FILE.exists():
        return None
    with open(config.TOKEN_FILE) as f:
        return json.load(f)


def save_tokens(token_response: dict) -> dict:
    now = time.time()
    record = {
        "access_token": token_response["access_token"],
        "refresh_token": token_response["refresh_token"],
        "token_type": token_response.get("token_type", "bearer"),
        "obtained_at": now,
        "expires_at": now + token_response.get("expires_in", 86400),
    }

    tmp_path = config.TOKEN_FILE.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(record, f, indent=2)
    os.replace(tmp_path, config.TOKEN_FILE)
    os.chmod(config.TOKEN_FILE, 0o600)

    return record


def is_expired(tokens: dict, buffer_seconds: int = 120) -> bool:
    return time.time() >= (tokens["expires_at"] - buffer_seconds)
